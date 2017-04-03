from selenium import webdriver

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase

from albums.models import Album
from albums.models import Track

from solos.models import Solo


class StudentTestCase(LiveServerTestCase):

    reset_sequences = True

    def setUp(self):
        self.browser = webdriver.Chrome()
        # self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(2)
        self.browser.set_window_size(1024, 1024)
        self.browser.set_window_position(0, 0)

        self.admin_user = get_user_model().objects.create_superuser(
            username='test_admin',
            email='test.admin@example.com',
            password='test_password'
        )

        from django.db import connection
        if connection.vendor == 'sqlite':
            with connection.cursor() as cursor:
                cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ= '0' WHERE NAME='albums_album'")

        self.album1 = Album.objects.create(
            name='My Favorite Things',
            slug='my-favorite-things'
        )
        self.track1 = Track.objects.create(
            name='My Favorite Things',
            slug='my-favorite-things',
            album=self.album1
        )
        self.solo1 = Solo.objects.create(
            instrument='saxophone',
            artist='John Coltrane',
            track=self.track1,
            slug='john-coltrane'
        )

        self.album2 = Album.objects.create(
            name='Kind of Blue',
            slug='kind-of-blue'
        )
        self.track2 = Track.objects.create(
            name='All Blues',
            slug='all-blues',
            album=self.album2,
            track_number=4
        )
        self.solo2 = Solo.objects.create(
            instrument='saxophone',
            artist='Cannonball Adderley',
            track=self.track2,
            start_time='4:05',
            end_time='6:04',
            slug='cannonball-adderley'
        )

        self.album3 = Album.objects.create(
            name='Know What I Mean?',
            slug='know-what-i-mean'
        )
        self.track3 = Track.objects.create(
            name='Waltz for Debby',
            slug='waltz-for-debby',
            album=self.album3
        )
        self.solo3 = Solo.objects.create(
            instrument='saxophone',
            artist='Cannonball Adderley',
            track=self.track3,
            slug='cannonball-adderley'
        )

        self.solo4 = Solo.objects.create(
            instrument='trumpet',
            artist='Miles Davis',
            track=self.track2,
            slug='miles-davis',
            start_time='1:46',
            end_time='4:04'
        )

        self.track4 = Track.objects.create(
            name='Freddie Freeloader',
            album=self.album2,
            track_number=2
        )

        self.track5 = Track.objects.create(
            name='Blue in Green',
            album=self.album2,
            track_number=3
        )

    def tearDown(self):
        self.browser.quit()

    def _find_search_results(self):
        return self.browser.find_elements_by_css_selector('.jmad-search-result a')

    def test_01_test_student_find_solos(self):
        """
        Test that a user can search for solos
        """

        # Steve is a jazz student who would like to find more
        # examples of solos so he can improve his own
        # improvisation.

        # He visits the home page of JMAD.
        self.browser.get(self.live_server_url + '/')

        # He knows he's in the right place because he can see
        # the name of the site in the heading.
        brand_element = self.browser.find_element_by_css_selector('.navbar-brand')
        self.assertEqual('JMAD', brand_element.text)

        # He sees the inputs of the search form, including
        # labels and placeholders.

        instrument_input = self.browser.find_element_by_css_selector('input#jmad-instrument')
        self.assertIsNotNone(
            self.browser.find_element_by_css_selector('label[for="jmad-instrument"]')
        )
        self.assertEqual(
            instrument_input.get_attribute('placeholder'),
            'i.e. trumpet'
        )

        artist_input = self.browser.find_element_by_css_selector('input#jmad-artist')
        self.assertIsNotNone(
            self.browser.find_element_by_css_selector('label[for="jmad-artist"]')
        )
        self.assertEqual(
            artist_input.get_attribute('placeholder'),
            'i.e. Davis'
        )

        # He types in the name of his instrument and submits it.
        instrument_input.send_keys('saxophone')
        self.browser.find_element_by_css_selector('form button').click()

        # He sees too many search results...
        search_results = self._find_search_results()
        self.assertGreater(len(search_results), 2)

        # ... so he adds a particular artist to his search query and
        # gets a more manageable list
        second_artist_input = self.browser.find_element_by_css_selector('input#jmad-artist')
        second_artist_input.send_keys('Cannonball Adderley')
        self.browser.find_element_by_css_selector('form button').click()
        second_search_results = self._find_search_results()
        self.assertEqual(len(second_search_results), 2)

        # He clicks on a search result.
        second_search_results[0].click()

        # On the solo page ...

        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + '/recordings/kind-of-blue/all-blues/cannonball-adderley/'
        )

        # he sees the artist...
        self.assertEqual(
            self.browser.find_element_by_css_selector('#jmad-artist').text,
            'Cannonball Adderley'
        )
        # the track title (with a count of solos)...
        self.assertEqual(
            self.browser.find_element_by_css_selector('#jmad-track').text,
            'All Blues [2 solos]'
        )

        # and the album title (with track count) for this solo.
        self.assertEqual(
            self.browser.find_element_by_css_selector('#jmad-album').text,
            'Kind of Blue [3 tracks]'
        )

    def test_02_staff_can_add_content(self):
        """
        Tests that a 'staff' user can access the admin and
        add Albums, Tracks, and Solos
        """
        # Bill would like to add a record and a number of
        # solos to JMAD. He visits the admin site

        admin_url = self.live_server_url + '/admin/'
        self.browser.get(admin_url)

        # He can tell he's in the right place because of the
        # title of the page

        self.assertEqual(self.browser.title, 'Log in | Django site admin')

        # He enters his username and password and submits the
        # form to log in

        login_form = self.browser.find_element_by_id('login-form')
        login_form.find_element_by_name('username').send_keys('test_admin')
        login_form.find_element_by_name('password').send_keys('test_password')
        login_form.find_element_by_css_selector('.submit-row input').click()

        # He sees links to Albums
        albums_link = self.browser.find_element_by_link_text('Albums')

        self.assertEqual(
            albums_link.get_attribute('href'),
            self.live_server_url + '/admin/albums/album/'
        )

        # He sees links to Tracks
        tracks_link = self.browser.find_element_by_link_text('Tracks')
        self.assertEqual(
            tracks_link.get_attribute('href'),
            self.live_server_url + '/admin/albums/track/'
        )

        # He sees links to Solos
        solos_link = self.browser.find_element_by_link_text('Solos')
        self.assertEqual(
            solos_link.get_attribute('href'),
            self.live_server_url + '/admin/solos/solo/'
        )

        # He clicks on Albums and sees all of the Albums that
        # have been added so far

        albums_link.click()

        self.assertEqual(
            self.browser.find_element_by_link_text('Know What I Mean?').get_attribute('href'),
            self.live_server_url + '/admin/albums/album/3/change/'
        )

        self.assertEqual(
            self.browser.find_element_by_link_text('Kind of Blue').get_attribute('href'),
            self.live_server_url + '/admin/albums/album/2/change/'
        )

        self.assertEqual(
            self.browser.find_element_by_link_text('My Favorite Things').get_attribute('href'),
            self.live_server_url + '/admin/albums/album/1/change/'
        )

        # Going back to the home page, he clicks the Tracks
        # link and sees the Tracks that have been added.
        # They're ordered first by Album, then by track
        # number.
        self.browser.find_element_by_css_selector('#site-name a').click()
        self.browser.find_element_by_link_text('Tracks').click()
        track_rows = self.browser.find_elements_by_css_selector('#result_list tr')

        self.assertEqual(track_rows[1].text, 'Kind of Blue Freddie Freeloader 2')
        self.assertEqual(track_rows[2].text, 'Kind of Blue Blue in Green 3')
        self.assertEqual(track_rows[3].text, 'Kind of Blue All Blues 4')
        self.assertEqual(track_rows[4].text, 'Know What I Mean? Waltz for Debby -')
        self.assertEqual(track_rows[5].text, 'My Favorite Things My Favorite Things -')

        # He adds a track to an album that already exists

        self.browser.find_element_by_link_text('ADD TRACK').click()
        track_form = self.browser.find_element_by_id('track_form')

        track_form.find_element_by_name('name').send_keys('So What')
        track_form.find_element_by_name('album').find_elements_by_tag_name('option')[1].click()
        track_form.find_element_by_name('track_number').send_keys('1')

        track_form.find_element_by_name('slug').send_keys('so-what')
        track_form.find_element_by_css_selector('.submit-row input').click()

        self.assertEqual(
            self.browser.find_elements_by_css_selector('#result_list tr')[1].text,
            'Kind of Blue So What 1'
        )

        # He adds another track, this time on an album that is not in JMAD yet

        self.browser.find_element_by_link_text('ADD TRACK').click()
        track_form = self.browser.find_element_by_id('track_form')
        track_form.find_element_by_name('name').send_keys('My Funny Valentine')

        # After adding the basic Track info, he clicks on the plus
        # sign to add a new album.

        track_form.find_element_by_id('add_id_album').click()

        # The focus shifts to the newly opened window, where he sees
        # an Album form

        self.browser.switch_to.window(self.browser.window_handles[1])
        album_form = self.browser.find_element_by_id('album_form')

        album_form.find_element_by_name('name').send_keys('Cookin\'')
        album_form.find_element_by_name('artist').send_keys('Miles Davis Quintet')
        album_form.find_element_by_name('slug').send_keys('cookin')
        album_form.find_element_by_css_selector('.submit-row input').click()

        # After creating the Album, he goes back to finish the Track

        self.browser.switch_to.window(self.browser.window_handles[0])
        track_form = self.browser.find_element_by_id('track_form')

        track_form.find_element_by_name('track_number').send_keys('1')
        track_form.find_element_by_name('slug').send_keys('my-funny-valentine')
        track_form.find_element_by_css_selector('.submit-row input').click()

        self.assertEqual(
            self.browser.find_elements_by_css_selector('#result_list tr')[1].text,
            'Cookin\' My Funny Valentine 1'
        )

        # He goes back to the root of the admin site and clicks on 'Solos'

        # DID NOT WORK self.browser.find_element_by_css_selector('#site-name a').click()
        self.browser.find_element_by_link_text('Home').click()
        # DID NOT WORK self.browser.find_elements_by_link_text('Solos')[1].click()
        self.browser.find_element_by_link_text('Solos').click()

        # He's sees Solos listed by Album, then Track, then start time

        solo_rows = self.browser.find_elements_by_css_selector('#result_list tr')

        self.assertEqual(
            solo_rows[1].text,
            'All Blues Miles Davis 1:46-4:04'
        )
        self.assertEqual(
            solo_rows[2].text,
            'All Blues Cannonball Adderley 4:05-6:04'
        )
        self.assertEqual(
            solo_rows[3].text.strip(),
            'Waltz for Debby Cannonball Adderley'
        )
        self.assertEqual(
            solo_rows[4].text.strip(),
            'My Favorite Things John Coltrane'
        )

        # He sees Solos listed by Album, then Track, then
        # start time

        # He adds a Solo to a Track that already exists

        # He then adds a Solo for which the Track and Album
        # do not yet exist

        # He adds a Track from the Solo page

        # He adds an Album from the Track popup

        # He finishes up both parent objects, and saves the
        # Solo

        # self.fail('Incomplete Test')
