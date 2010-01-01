from datetime import datetime
import urllib
import logging
import hashlib
import re

from django.db import models
from django.contrib import admin
from django.utils.encoding import smart_unicode
from django.template import Template

from gazjango.community.sources import utils
from gazjango.community.models import Entry

log = logging.getLogger('community.sources.flickr')

# model definition
class FlickrPhoto(Entry):
    photo_id    = models.CharField(max_length=200,)
    server      = models.IntegerField(null=True,blank=True)
    secret      = models.CharField(max_length=200,null=True,blank=True)

    original_secret = models.CharField(max_length=200,null=True,blank=True)
    original_format = models.CharField(max_length=4,null=True,blank=True)
    num_comments= models.IntegerField(blank=True, null=True)

    taken_at    = models.DateTimeField(null=True,blank=True)
    uploaded_at = models.DateTimeField(null=True,blank=True)

    exif        = models.TextField(blank=True, null=True, )

    class Meta:
        ordering = ['-uploaded_at']
        unique_together = [('photo_id', 'server'),]
        app_label = "community"

    def __unicode__(self):
        return self.title

    @property
    def photog(self):
        return self.owner_user

    @property
    def format_template(self):
        return Template("<div class = 'entry photo'><a href='{{ curr_object.url }}'><img src='{{ curr_object.square }}' /> {{ curr_object.title }}</a></div>")
    
    # image urls
    @property
    def image(self):
        """ this is a 500px (longest side) image """
        return self._build_image_url()
    @property
    def thumbnail(self):
        """ this is a 100px (longest side) image """
        return self._build_image_url('t')
    @property
    def square(self):
        """ this is a 75x75 image """
        return self._build_image_url('s')
    @property
    def small(self):
        """ this is a 240px (longest side) image """
        return self._build_image_url('m')
    @property
    def large(self):
        """ this is a 1024 (longest side) image """
        return self._build_image_url('b')

    def _build_image_url(self, size=None):
        if size in list('stmb'):
            return "http://static.flickr.com/%s/%s_%s_%s.jpg" % (self.server, self.photo_id, self.secret, size)
        return "http://static.flickr.com/%s/%s_%s.jpg" % (self.server, self.photo_id, self.secret)

# retrieve function, this is how we handle items
def retrieve(force, **args):
    """ this is how we will handle photos """

    username, user_id = args['account']
    flickr = FClient(args['api_key'])

    last_update = datetime.fromtimestamp(0)
    if force:
        log.info("Forcing update of all available photos")
    else:
        try:
            last_update = FlickrPhoto.objects.filter(owner_user=username).order_by('-uploaded_at')[0].uploaded_at
        except Exception, e:
            log.debug("%s", e)

    log.debug('last update: %s', last_update)
    page = 1

    while True:
        res = flickr.exe_method(
            'groups.pools.getPhotos', 
            group_id="89729977@N00",
            api_key="4b27219ffc49d3fbe5d2fcf3a4d411f7", 
            extras="date_taken,last_update", 
            per_page='500', 
            page=page
        )
        if res is False:
            log.error('error')
            break

        res = res['photos']
        for photo in res['photo']:
            photo_up_time = datetime.fromtimestamp(float(photo['lastupdate']))
            if last_update <= photo_up_time:
                log.debug('current photo upload time: %s', photo_up_time)
                _handle_photo(flickr, photo, username)
            else:
                break
        page += 1

        if page > res['pages']:
            log.info('no more photos')
            break

class FClient(object):
    def __init__(self, api_key):
        self.api_key = api_key

        self.method = 'flickr'
        self.format = 'json'
        self.nojsoncallback = '1'

        log.debug('flickrclient created.')

    def exe_method(self, method, **kwargs):
        kwargs['method']    = '%s.%s' % (self.method,method)
        kwargs['api_key']   = self.api_key
        kwargs['format']    = self.format
        kwargs['nojsoncallback']= self.nojsoncallback

        url = "http://api.flickr.com/services/rest/?"
        
        for k,v in kwargs.iteritems():
            kwargs[k] = v

        res = utils.get_remote_data(url + urllib.urlencode(kwargs), rformat='json')
        
        if res.get("stat", "") == "fail":
            log.error("flickr retrieve failed.")
            log.error("%s" % res.get("stat"))
            return False

        return res

    def sign(self, dictionary):
        data = [self.secret]
        for key in sorted(dictionary.keys()):
            data.append(key)
            datum = dictionary[key]
            if isinstance(datum, unicode):
                raise IllegalArgumentException("No Unicode allowed, "
                        "argument %s (%r) should have been UTF-8 by now"
                        % (key, datum))
            data.append(datum)
        
        return hashlib.md5(''.join(data)).hexdigest()

    def encode_and_sign(self, **kwargs):
        '''URL encodes the data in the dictionary, and signs it using the
        given secret, if a secret was given.
        '''
        
        dictionary = make_utf8(kwargs)
        if self.secret:
            dictionary['api_sig'] = self.sign(dictionary)
        return urllib.urlencode(dictionary)

def _handle_photo(flickr_obj, photo, user):
    photo_id        = photo['id']

    log.info('working with photo => id: %s', photo_id)

    info = flickr_obj.exe_method('photos.getInfo', photo_id=photo_id)['photo']
    photo_obj, created = FlickrPhoto.objects.get_or_create(
        photo_id    = photo_id,
        timestamp   = datetime.fromtimestamp(utils.safeint(info["dates"]["posted"]))
    )


    photo_obj.taken_at    = photo['datetaken']
    photo_obj.source_type = "flickrphoto"
    photo_obj.timestamp   = datetime.fromtimestamp(utils.safeint(info["dates"]["posted"]))
    photo_obj.uploaded_at = datetime.fromtimestamp(utils.safeint(info["dates"]["posted"]))
    photo_obj.owner_user  = photo['owner']

    try:
        photo_obj.url               = "http://www.flickr.com/photos/%s/%s" % (photo_obj.owner_user, photo_obj.photo_id)
        photo_obj.server            = utils.safeint(smart_unicode(photo['server']))
        photo_obj.taken_at          = photo['datetaken']
        photo_obj.secret            = photo['secret']
        photo_obj.title             = smart_unicode(photo['title'])
        photo_obj.description       = smart_unicode(info['description']['_content'])
        photo_obj.num_comments      = utils.safeint(info["comments"]["_content"])
        photo_obj.save()
    except Exception, e:
        log.error('%s' % e)


def make_utf8(dictionary):
    '''Encodes all Unicode strings in the dictionary to UTF-8. Converts
    all other objects to regular strings.

    Returns a copy of the dictionary, doesn't touch the original.
    '''

    result = {}

    for (key, value) in dictionary.iteritems():
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        else:
            value = str(value)
        result[key] = value

    return result
