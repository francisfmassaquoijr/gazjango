#!/usr/bin/env python

import settings
from django.core.management import setup_environ
setup_environ(settings)

from datetime                   import date, timedelta
from django.contrib.auth.models import User, Group

from accounts.models            import UserProfile, Position
from articles.models            import Article, Category, Format
from articles.models            import Announcement, AnnouncementKind
from issues.models              import Issue
from polls.models               import Poll, Option
import tagging


### Groups

reader_group       = Group.objects.create(name="Readers")
reporter_group     = Group.objects.create(name="Reporters")
photographer_group = Group.objects.create(name="Photographers")
editor_group       = Group.objects.create(name="Editors")
admin_group        = Group.objects.create(name="Admins")


### Users

def make_user(username, email, first, last, phone=None, contact=None, bio=None, groups=None):
    user = User.objects.create_user(username, email)
    user.userprofile_set.add(UserProfile(phone=phone, contact=contact, bio=bio))
    user.first_name = first
    user.last_name  = last
    if groups:
        user.groups = groups
    user.save()
    return user

bob  = make_user('bob', 'bob@example.com', 'Bob', 'Jones', 
                 '123-456-7890', 'AIM: bobjones52', groups=[reader_group, editor_group])
jack = make_user('jack', 'jack@uppityup.com', 'Jack', 'McSmith', 
                 bio="I'm pretty much the man.", groups=[reader_group, photographer_group, editor_group])
jill = make_user('jill', 'jill@thehill.com',  'Jill', 'Carnegie', 
                 contact="GTalk: jill@thehill.com", groups=[reader_group, admin_group])
bone = make_user('bone', 'doctress@example.com', 'The', 'Bone Doctress', 
                 bio="I'm a mysterious figure.", groups=[reader_group, reporter_group])
angry = make_user('angry', 'somedude@swat.net', 'Angry', 'Man',
                 bio="I used to be in charge of this paper, but I've since moved "
                     "on to bigger and better things: complaining and nitpicking.",
                 groups=[reader_group])

### Positions

reader          = Position.objects.create(name="Reader")
columnist       = Position.objects.create(name="Columnist")
reporter        = Position.objects.create(name="Staff Reporter")
photographer    = Position.objects.create(name="Staff Photographer")
bossman         = Position.objects.create(name="Editor-In-Chief")
news_editor     = Position.objects.create(name="News Editor")
arts_editor     = Position.objects.create(name="Arts Editor")
features_editor = Position.objects.create(name="Features Editor")
photo_editor    = Position.objects.create(name="Photography Editor")
tech_director   = Position.objects.create(name="Technical Director")


### Users' having Positions
bob_p = bob.get_profile()
jack_p = jack.get_profile()
jill_p = jill.get_profile()
bone_p = bone.get_profile()
angry_p = angry.get_profile()

bob_p.add_position(reader,      date(2005, 9, 1), date(2006, 9, 1))
bob_p.add_position(reporter,    date(2006, 9, 1), date(2007, 9, 1))
bob_p.add_position(news_editor, date(2007, 9, 1))

jack_p.add_position(photographer, date(2006, 9, 1))
jack_p.add_position(photo_editor, date(2007, 12, 4))

jill_p.add_position(reporter,    date(2004, 9, 1), date(2005, 9, 1))
jill_p.add_position(arts_editor, date(2005, 9, 1), date(2006, 9, 1))
jill_p.add_position(bossman,     date(2006, 9, 1))

bone_p.add_position(reader,    date(2006, 9, 1))
bone_p.add_position(columnist, date(2008, 1, 21))

angry_p.add_position(bossman, date(2002, 9, 1), date(2006, 9, 1))
angry_p.add_position(reader,  date(2006, 9, 1))


### Categories

news     = Category.objects.create(name="News", slug="news",
                                   description="What's going on in the world.")
features = Category.objects.create(name="Features", slug="features",
                                   description="The happenings around town.")
opinions = Category.objects.create(name="Opinions", slug="opinions",
                                   description="What people have to say.")
columns  = Category.objects.create(name="Columns", slug="columns",
                                   description="Foreign countries, sex, or both.")
bone_doctress = Category.objects.create(name="The Bone Doctress", 
                                   slug="bone_doctress",
                                   description="Everyone's favorite sex column.")

### Formats
textile = Format.objects.create(name="Textile", function="textile")
html    = Format.objects.create(name="Raw HTML", function="html")


### Articles

nobody_loves_me = Article.objects.create(
    headline="Nobody Loves Me",
    subtitle="It's True: Not Like You Do",
    slug='no_love',
    category=bone_doctress,
    summary="The Bone Doctress takes a break from her usual witty recountings of "
            "sexual escapades to share with you the lyrics to a Portishead song.",
    format=textile
)
nobody_loves_me.authors.add(bone_p)
nobody_loves_me.text = """To pretend no one can find
The fallacies of morning rose
Forbidden fruit, hidden eyes
Curtises that I despise in me
Take a ride, take a shot now

Cos nobody loves me
Its true
Not like you do

Covered by the blind belief
That fantasies of sinful screens
Bear the facts, assume the dye
End the vows no need to lie, enjoy
Take a ride, take a shot now

Cos nobody loves me
Its true
Not like you do

Who oo am I, what and why
Cos all I have left is my memories of yesterday
Ohh these sour times

Cos nobody loves me
Its true
Not like you do

After time the bitter taste
Of innocence decent or race
Scattered seeds, buried lives
Mysteries of our disguise revolve
Circumstance will decide ....

Cos nobody loves me
Its true
Not like you do

Cos nobody loves me
Its true
Not like you
Nobody loves.. me
Its true
Not, like, you.. do"""
nobody_loves_me.revise_text( nobody_loves_me.text +  
  "\n\nSorry I forgot to cite! Hehe, no plagiarism plz. its by portishead, "
  "called nobody loves me or sour times or somethyng, off dummy i think. mebbe "
  "portishead. actually yeah i think its off theyr secund album. lawl. kkthx.")
nobody_loves_me.tags = "music"
nobody_loves_me.save()


scandal = Article.objects.create(
    headline="Al Bloom Pressured Out By Board of Managers",
    subtitle="Allegations of Involvement with Empereror's Club VIP Surface",
    slug="bloom_scandal",
    category=news,
    summary="A Daily Gazette investigation has uncovered allegations that "
            "Al Bloom was involved in the Emperor's Club VIP scandal. Some say"
            "this is related to his recent resignation.",
    text="An investigation by the Gazette has uncovered connections between Al "
         "Bloom and the Emperor's Club VIP. Photos have surfaced that show him "
         "clearly engaging in unseemly acts with a woman who looks suspiciously "
         "like former New York governor Spitzer's pricey prostitute.\n\nA senior "
         "member of the Board of Managers, who wished to remain anonymous, supplied "
         "these photos to the community through an online forum and claimed that "
         "they were the true reason behind Al Bloom's unexpected retirement.\n\nThe "
         "College and other Board members refused comment. Some students, however, "
         "have expressed concern that the photos may be fake: \"I can tell by the "
         "pixels,\" claimed one rising senior, \"and by having seen a few 'shops "
         "in my time.\"\n\nThe Gazette will have more on this story as information "
         "becomes available.\n\n[source: http:\/\/dailyjolt.com]",
    format=textile
)
scandal.authors.add(bob_p, jack_p)
scandal.tags = "Al Bloom, Board of Managers, Daily Jolt"
scandal.save()


### Announcements

community = AnnouncementKind.objects.create(name="Community",
                  description="Announcements from the greater Swarthmore community.")
staff     = AnnouncementKind.objects.create(name="Staff",
                  description="Announcements from the Daily Gazette.")

Announcement.objects.create(
    kind=staff, 
    slug="summer_return",
    text="We're up and publishing for a very special summer term! This is a "
         "very special term, though, so only a select handful get to read us "
         "right now...or ever.",
    date_end = date.today() + timedelta(days=1)
)

Announcement.objects.create(
    kind=community,
    slug="cookies",
    date_end = date.today() + timedelta(days=10),
    text="There will be cookies in each and every cabinet across campus, "
         "courtesy of the Summer Cookie Faries. Get them while they last!"
)


### Polls

jolt_poll = Poll.objects.create(
    name = "Is the Daily Jolt a legitimate news source?",
    slug = "is_jolt_legit",
    question = "We got most (read: all) of our information from this article "
               "from the Daily Jolt. Is that okay?",
    allow_anon = True,
    article = scandal
)

jolt_yes   = Option.objects.create(name="yes", poll=jolt_poll,
    description = "Absolutely. Don't you know that's where CNN gets its news?")
jolt_no    = Option.objects.create(name="no",  poll=jolt_poll,
    description = "No way. Don't you know that's where CNN gets its news?")
jolt_maybe = Option.objects.create(name="maybe", poll=jolt_poll,
    description = "Critical thinking is hard. Let's go shopping!")

jolt_poll.vote(bob, jolt_yes)
jolt_poll.vote(jack, jolt_yes)
jolt_poll.vote(jill, jolt_no)
jolt_poll.vote(bone, jolt_maybe)


### Issues

issue_today = Issue.objects.create(
    menu="Sharples is closed, sucka!",
    weather = "Today: very happy.\n"
              "I don't like writing weather jokes.\n"
              "\n"
              "Tonight: very sad.\n"
              "And nobody's going to complain if there isn't one here.\n"
              "\n"
              "Tomorrow: happy and sad at the same time.\n"
              "So why would I bother to write a real one?",
    events = "Nothing's happening."
)
issue_today.add_article(scandal)
issue_today.add_article(nobody_loves_me)