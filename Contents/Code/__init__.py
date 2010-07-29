import re, sys, encodings.idna
from PMS import Plugin, Log, DB, Thread, XML, HTTP, JSON, RSS, Utils
from PMS.MediaXML import MediaContainer, DirectoryItem, VideoItem, SearchDirectoryItem
from PMS.Shorthand import _L, _R

import urllib, htmlentitydefs, datetime

TED_PLUGIN_PREFIX   = "/video/TED"
TED_ROOT            = "http://www.ted.com/index.php/talks/list"
TED_BASE            = "http://www.ted.com/index.php/"
CACHE_TIME          = 3600 * 12

dirs = [ ['Newest releases', 'NEWEST'], ['Date filmed', 'FILMED'], ['Most emailed' , 'MOSTEMAILED'], ['Most discussed' , 'MOSTDISCUSSED'], ['Most favorited' , 'MOSTFAVORITED'], ['Rated most jaw-dropping' , 'JAW-DROPPING'], ['Rated most persuasive' , 'PERSUASIVE'], ['Rated most courageous' , 'COURAGEOUS'], ['Rated most ingenious' , 'INGENIOUS'], ['Rated most fascinating' , 'FASCINATING'], ['Rated most inspiring' , 'INSPIRING'], ['Rated most beautiful' , 'BEAUTIFUL'], ['Rated funniest' , 'FUNNY'] ]

sections = [ ['Top Twelves', 'talks/list'], ['All Talks', 'talks/list'], ['Themes', 'themes/list'], ['Tags', 'talks/tags'], ['Speakers', 'speakers/browse'] ]

####################################################################################################
def Start():
  Plugin.AddRequestHandler(TED_PLUGIN_PREFIX, HandleVideosRequest, "TED Talks", "icon-default.png", "art-default.png")
  Plugin.AddViewGroup("Details", viewMode="InfoList", contentType="items")

####################################################################################################
def HandleVideosRequest(pathNouns, count):
  for p in pathNouns:
    Log.Add("$pathNouns : " + Utils.DecodeUrlPathToString(p))
  dir = MediaContainer("art-default.png", None, "TED Talks")
  dir.SetAttr("content", "items")
  Log.Add("Count: " + str(count))
  # Top level menu
  if count == 0:
    for (n,v) in sections:
      dir.AppendItem(DirectoryItem(Utils.EncodeStringToUrlPath(v+"$"+n), n, ""))

  # Section menu.
  elif count == 1:
      (theSection,name) = Utils.DecodeUrlPathToString(pathNouns[0]).split('$')
      dir.SetAttr("title2", name)

      try:
        pageCount = re.sub(r'.*?(\d+)$', r'\1', GetXML(TED_BASE + theSection, True).xpath("//div[@class='pagination clearfix']/p")[0].text)
      except:
        pageCount = 1
      Log.Add("Page count: " + str(pageCount))

      if name == 'Tags':
        for pageNum in range(1, int(pageCount) + 1):
          try:
            for anItem in GetXML(TED_BASE + theSection + '/page/' + str(pageNum), True).xpath("//div[@class='column']/div/ul/li/a"):
              url = anItem.get('href')
              title = anItem.text
              dir.AppendItem(DirectoryItem(Utils.EncodeStringToUrlPath(url) + '$' + title, title, ''))
          except:
            pass
      elif name == 'Top Twelves':
        for (n,v) in dirs:
          dir.AppendItem(DirectoryItem(Utils.EncodeStringToUrlPath(v + "$" + n), n, ""))
      elif name == 'All Talks':
        for pageNum in range(1, int(pageCount) + 1):
          try:
            for v in GetXML(TED_ROOT + '/page/' + str(pageNum), True).xpath("//div[@class='browser']/div/dl"):
              dir.AppendItem(getVideoPageContents(scrapeVideoListingContents(v, True, False)))
          except:
            pass
        #dir = getVideoPage(pathNouns[1])
      elif name == 'Speakers':
        for pageNum in range(1, int(pageCount) + 1):
          #try:
          for v in GetXML(TED_BASE + theSection + '?event=0&tagid=0&alphabyfirstname=all&orderedby=ALPHABET&page=' + str(pageNum), True).xpath("//div[@class='speakerListContainer clearfix']/dl"):
            dir.AppendItem(scrapeVideoListing(v, False, False, hasConferenceTitle=False))
          #except:
            #pass
      elif name == 'Themes':
        for pageNum in range(1, int(pageCount) + 1):
          #try:
          for v in GetXML(TED_BASE + theSection + '/page/' + str(pageNum), True).xpath("//div[@class='themeListContainer clearfix']/dl"):
            Log.Add(v)
            dir.AppendItem(scrapeVideoListing(v, False, False, hasConferenceTitle=False))
          #except:
            #pass

  # Directory.
  elif count == 2:
    (theSection,name1) = Utils.DecodeUrlPathToString(pathNouns[0]).split('$')

    if name1 == 'Top Twelves':
      (val,name) = Utils.DecodeUrlPathToString(pathNouns[1]).split('$')
      dir.SetAttr("title2", name)
      for v in XML.ElementFromURL(TED_ROOT + '?viewtype=list&orderedby=' + val, True).xpath('//div[@class="browser"]/div/dl'):
        dir.AppendItem(getVideoPageContents(scrapeVideoListingContents(v, True, False)))
    #elif name1 == 'All Talks':
      #dir = getVideoPage(pathNouns[1])
    elif name1 == 'Speakers':
      (val,duration,thumb,title) = pathNouns[1].split('$')
      dir.SetAttr("title2", Utils.DecodeUrlPathToString(title))
      for v in XML.ElementFromString(getFixedPage("http://www.ted.com" + Utils.DecodeUrlPathToString(val)), True).xpath('//dl[@class="box clearfix"]'):
        #dir.AppendItem(scrapeVideoListing(v, True, False, hasConferenceTitle=False))
        dir.AppendItem(getVideoPageContents(scrapeVideoListingContents(v, True, False, hasConferenceTitle=False)))
    elif name1 == 'Themes':
      (val,duration,thumb,title) = pathNouns[1].split('$')
      dir.SetAttr("title2", Utils.DecodeUrlPathToString(title))

      jsonPage = GetFixedXML("http://www.ted.com" + Utils.DecodeUrlPathToString(val), True).xpath('//div[@class="speakers"]/script[2]')[0].text
      jsonPage = jsonPage.split("\n")[2]
      jsonPage = re.sub(r'\s+var dsTalks = new YAHOO\.util\.DataSource\("([^"]+)"\).*', r'\1', jsonPage)
      jsonPage = 'http://www.ted.com' + jsonPage
      Log.Add(jsonPage)
      dict = JSON.DictFromURL(jsonPage)
      for v in dict[u'resultSet'][u'result']:
        dir.AppendItem(getVideoPageContents(scrapeJSONlisting(v)))
      for v in GetFixedXML("http://www.ted.com" + Utils.DecodeUrlPathToString(val), True).xpath('//div[@class="clearfix"]/dl'):
        dir.AppendItem(getVideoPageContents(scrapeVideoListingContents(v, True, True)))
        #dir.AppendItem(scrapeVideoListing(v, True, True))
    elif name1 == 'Tags':
      (val,name) = pathNouns[1].split('$')
      dir.SetAttr("title2", name)
      try:
        pageCount = re.sub(r'.*?(\d+)$', r'\1', XML.ElementFromURL("http://www.ted.com" + Utils.DecodeUrlPathToString(val), True).xpath("//div[@class='pagination clearfix']/p")[0].text)
        Log.Add("Page count: " + str(pageCount))
      except:
        pageCount = 1
      for pageNum in range(1, int(pageCount) + 1):
        for v in GetFixedXML("http://www.ted.com" + Utils.DecodeUrlPathToString(val) + '/page/' + str(pageNum), True).xpath('//div[@class="clearfix"]/dl'):
          dir.AppendItem(getVideoPageContents(scrapeVideoListingContents(v, True, False, 'h3', False)))
          #dir.AppendItem(scrapeVideoListing(v, True, False, 'h3', False))

  # Video page.
  #elif count == 3:
    #dir = getVideoPage(pathNouns[2])

  return dir.ToXML()

####################################################################################################
def scrapeVideoListing(v, hasPlayImg, hasDuration, heading='h4', hasConferenceTitle=True):
  if hasPlayImg:
    thumb = v.xpath('dt/a/img[2]')[0].get('src')
  else: thumb = v.xpath('dt/a/img')[0].get('src')
  url = v.xpath('dt/a')[0].get('href')
  if not hasDuration:
    duration = 0
  else:
    duration = v.xpath('dd/ul/li[2]/div/em')[0].text.split()[0].split(':')
    duration = (int(duration[0])*60 + int(duration[1])) * 1000
  if hasConferenceTitle:
    title = v.xpath('dd/' + heading + '/a')[0].text.encode('ascii','ignore')
  else:
    title = v.xpath('dd/ul/li/' + heading + '/a')[0].text.encode('ascii','ignore')
  return DirectoryItem(Utils.EncodeStringToUrlPath(url) + '$' + str(duration) + '$' + Utils.EncodeStringToUrlPath(thumb) + '$' + Utils.EncodeStringToUrlPath(title), title, thumb)

def scrapeVideoListingContents(v, hasPlayImg, hasDuration, heading='h4', hasConferenceTitle=True):
  if hasPlayImg:
    thumb = v.xpath('dt/a/img[2]')[0].get('src')
  else: thumb = v.xpath('dt/a/img')[0].get('src')
  url = v.xpath('dt/a')[0].get('href')
  if not hasDuration:
    duration = 0
  else:
    duration = v.xpath('dd/ul/li[2]/div/em')[0].text.split()[0].split(':')
    duration = (int(duration[0])*60 + int(duration[1])) * 1000
  if hasConferenceTitle:
    title = v.xpath('dd/' + heading + '/a')[0].text.encode('ascii','ignore')
  else:
    title = v.xpath('dd/ul/li/' + heading + '/a')[0].text.encode('ascii','ignore')
  return url + '$' + str(duration) + '$' + thumb + '$' + title

####################################################################################################
def getVideoPage(pathNoun):
  (url,duration,thumb,title) = pathNoun.split('$')
  title = Utils.DecodeUrlPathToString(title)
  dir = MediaContainer("art-default.png", "Details", "TED Talks", title)
  page = XML.ElementFromURL('http://www.ted.com' + Utils.DecodeUrlPathToString(url), True)
  try:
    summary = ' '.join([e.text.strip() for e in page.xpath("id('tagline')")])
  except:
    summary = ''

  key = None
  for a in page.xpath('//dl[@class="downloads"]/dt/a'):
    if a.get('href').find('/talks/download/video') != -1:
      key = a.get('href')

  if key is not None:
    key = 'http://www.ted.com' + key

  title = page.xpath("id('body')/h1/span")[0].text.strip()
  Log.Add((key, title, summary, duration, Utils.DecodeUrlPathToString(thumb)))
  dir.AppendItem(VideoItem(key, title, summary, duration, Utils.DecodeUrlPathToString(thumb)))
  return dir

def getVideoPageContents(pathNoun):
  (url,duration,thumb,title) = pathNoun.split('$')
  dir = MediaContainer("art-default.png", "Details", "TED Talks", title)
  page = XML.ElementFromURL('http://www.ted.com' + url, True)
  try:
    summary = ' '.join([e.text.strip() for e in page.xpath("id('tagline')")])
  except:
    summary = ''

  key = None
  for a in page.xpath('//dl[@class="downloads"]/dt/a'):
    if a.get('href').find('/talks/download/video') != -1:
      key = a.get('href')

  if key is not None:
    key = 'http://www.ted.com' + key

  title = page.xpath("id('body')/h1/span")[0].text.strip()
  return VideoItem(key, title, summary, duration, thumb)
  #dir.AppendItem(VideoItem(key, title, summary, duration, thumb))
  #return dir

####################################################################################################
def scrapeJSONlisting(item):
  page = XML.ElementFromString(descape(item[u'markup']), True)
  return scrapeVideoListing(page, True, False)

####################################################################################################
def GetXML(url, use_html_parser=False):
  Plugin.Dict["CacheWorkaround"] = datetime.datetime.now()
  return XML.ElementFromString(HTTP.GetCached(url,CACHE_TIME), use_html_parser)

####################################################################################################
def GetFixedXML(url, use_html_parser=False):
  Plugin.Dict["CacheWorkaround"] = datetime.datetime.now()
  return XML.ElementFromString(descape(HTTP.GetCached(url,CACHE_TIME)), use_html_parser)

####################################################################################################
def getFixedPage(url):
  f = urllib.FancyURLopener().open(url)
  p = f.read()
  f.close()
  return(descape(p))

####################################################################################################
def descape_entity(m, defs=htmlentitydefs.entitydefs):
  entity = m.group(1)
  if entity == "raquo":
    return "_"
  if entity == "nbsp":
    return " "

  return m.group(0)
#  if entity == "lt" or entity == "amp" or entity == "gt" or entity == "quot" or entity == "apos": return(m.group(0))
#  try:
#    return defs[m.group(1)]
#  except KeyError:
#    return m.group(0) # use as is

####################################################################################################
def descape(string):
  pattern = re.compile("&(\w+?);")
  return pattern.sub(descape_entity, string)

