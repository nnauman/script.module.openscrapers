# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    OpenScrapers Project
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.domains = ['yts.ws']
		self.base_link = 'https://yts.ws'
		self.search_link = '/movie/%s'
		# self.search_link = '/search?search=%s'


	def movie(self, imdb, title, localtitle, aliases, year):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def sources(self, url, hostDict, hostprDict):
		try:
			sources = []

			if url is None:
				return sources

			if debrid.status() is False:
				return sources

			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

			title = data['title'].replace('&', 'and')
			hdlr = data['year']

			query = '%s %s' % (title, hdlr)
			query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

			url = self.search_link % urllib.quote(query)
			url = urlparse.urljoin(self.base_link, url).replace('%20', '-')
			# log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

			html = client.request(url)
			if html is None:
				return sources

			quality_size = client.parseDOM(html, 'p', attrs={'class': 'quality-size'})

			tit = client.parseDOM(html, 'title')[0]

			try:
				results = client.parseDOM(html, 'div', attrs={'class': 'ava1'})
			except:
				return sources

			p = 0
			for torrent in results:
				link = re.findall('a data-torrent-id=".+?" href="(magnet:.+?)" class=".+?" title="(.+?)"', torrent, re.DOTALL)

				for url, ref in link:
					url = str(client.replaceHTMLCodes(url).split('&tr')[0])

					name = url.split('&dn=')[1]
					name = urllib.unquote_plus(name).replace(' ', '.')
					if source_utils.remove_lang(name):
						continue

					t = name.split(hdlr)[0].replace('&', 'and').replace('.US.', '.').replace('.us.', '.')
					if cleantitle.get(t) != cleantitle.get(title):
						continue

					if hdlr not in tit:
						continue

					quality, info = source_utils.get_release_quality(ref, url)

					try:
						size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', quality_size[p])[-1]
						dsize, isize = source_utils._size(size)
						info.insert(0, isize)
					except:
						pass

					p += 1
					info = ' | '.join(info)

					sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': url,
												'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
			return sources

		except:
			source_utils.scraper_error('YTSWS')
			return sources


	def resolve(self, url):
		return url
