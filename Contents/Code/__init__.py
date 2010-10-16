import re

###################################################################################################

PLUGIN_TITLE               = 'TED talks'
VIDEO_PREFIX              = '/video/TED'

TED_BASE        ="http://www.ted.com"
TED_TALKS       ="http://www.ted.com/talks"
TED_THEMES      ="http://www.ted.com/themes/atoz"
TED_TAGS        ="http://www.ted.com/talks/tags"
TED_SPEAKERS    ="http://www.ted.com/speakers/atoz/page1"

# Default artwork and icon(s)
TEDart             = 'art-default.jpg'
TEDthumb        = 'icon-default.jpg'


###################################################################################################
def Start():
  Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, 'TED Talks',TEDthumb,TEDart)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
  
  MediaContainer.art        =R(TEDart)
  MediaContainer.title1     =PLUGIN_TITLE
  DirectoryItem.thumb       =R(TEDthumb)

  
####################################################################################################

def VideoMainMenu():
    dir = MediaContainer(mediaType='video') 
    dir.Append(Function(DirectoryItem(FrontPageList, "Front Page"), pageUrl = TED_BASE))
    dir.Append(Function(DirectoryItem(ThemeList, "Themes"), pageUrl = TED_THEMES))
    dir.Append(Function(DirectoryItem(TagsList, "Tags"), pageUrl = TED_TAGS))
    dir.Append(Function(DirectoryItem(SpeakersList, "Speakers"), pageUrl = TED_SPEAKERS))
    
    return dir
####################################################################################################

def SpeakersList(sender,pageUrl):
   
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")
    
    content = HTML.ElementFromURL(pageUrl)
    page=HTTP.Request(pageUrl)

    
    for speakers in content.xpath('//div[@id="maincontent"]/div/div/div/ul/li/a'):
        #Log(tags)
        speakerurl=TED_BASE+speakers.get('href')
        speakername=speakers.text
        fname=speakername.split(" ")[0]
        lname=speakername.split(" ")[1]
        if fname=="":
          speakername=lname
        else:
          speakername=lname + ", " + fname
        #taken out becuase it was infinitely slower
        #thumb=HTML.ElementFromURL(speakerurl).xpath('//link[@rel="image_src"]')[0].get('href')
        dir.Append(Function(DirectoryItem(speakertalks, title=speakername), pageUrl = speakerurl))
    

    try:
        next=TED_BASE + content.xpath('//a[@class="next"]')[0].get('href')
        dir.Append(Function(DirectoryItem(SpeakersList, title="Next page ..."), pageUrl = next))
    except: pass
    return dir

####################################################################################################

def speakertalks(sender,pageUrl):

    dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
    
    pageUrl=pageUrl.replace("&#13","")
    content = HTML.ElementFromURL(pageUrl).xpath('//dl[@class="box clearfix"]')
    page=HTTP.Request(pageUrl)

    count=-1
    
    for boxes in content:
      count=count+1
      for things in boxes[0]:
         thumb=things.xpath("img")[1].get('src')
      for things in boxes[1]:
         link=things.xpath('//ul/li/h4/a')[count].get('href')
         title=things.xpath('//ul/li/h4/a')[count].text
         subtitle=things.xpath('//ul/li/em')[count].text
         link=TED_BASE + link
         vidUrl=link     
         content=HTML.ElementFromURL(vidUrl).xpath('//dl[@class="downloads"]')[0].xpath('//dt')[4]
         vidUrl2=content[0].get('href')
         link=vidUrl2
         trueUrl="http://www.ted.com" + link + "#.mp4"
         dir.Append(VideoItem((trueUrl), title=title,subtitle=subtitle, thumb=thumb))

    return dir    
####################################################################################################

def FrontPageList(sender,pageUrl):
   
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")
    
    dir.Append(Function(DirectoryItem(FrontPageSort, "Technology"), pageUrl = "1"))
    dir.Append(Function(DirectoryItem(FrontPageSort, "Entertainment"), pageUrl = "2"))
    dir.Append(Function(DirectoryItem(FrontPageSort, "Design"), pageUrl = "3"))
    dir.Append(Function(DirectoryItem(FrontPageSort, "Business"), pageUrl = "4"))
    dir.Append(Function(DirectoryItem(FrontPageSort, "Science"), pageUrl = "5"))
    dir.Append(Function(DirectoryItem(FrontPageSort, "Global Issues"), pageUrl = "7"))
    dir.Append(Function(DirectoryItem(FrontPageSort, "All"), pageUrl = "0"))
    
    return dir
####################################################################################################

def FrontPageSort(sender,pageUrl):
    
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")
    id=pageUrl
    
    newest="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=NEWEST"
    mosttrans="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=MOSTTRANSLATED"
    mostemail="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=MOSTEMAILED"
    mostdisc="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=MOSTDISCUSSED"
    mostfav="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=MOSTFAVORITED"
    jawdrop="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=JAW-DRAPPING"
    persu="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=PERSUASIVE"
    courage="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=COURAGEOUS"
    ingen="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=INGENIOUS"
    fasc="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=FASCINATING"
    inspi="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=INSPIRING"
    beaut="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=BEAUTIFUL"
    funny="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=FUNNY"
    infor="http://www.ted.com/talks/searchRpc?tagid=" + id + "&orderedby=INFORMATIVE"
    
    dir.Append(Function(DirectoryItem(gettalks, "Newest releases"), pageUrl = newest))
    dir.Append(Function(DirectoryItem(gettalks, "Most Languages"), pageUrl = mosttrans))
    dir.Append(Function(DirectoryItem(gettalks, "Most emailed this week"), pageUrl = mostemail))
    dir.Append(Function(DirectoryItem(gettalks, "Most comments this week"), pageUrl = mostdisc))
    dir.Append(Function(DirectoryItem(gettalks, "Most favorited of all-time"), pageUrl = mostfav))
    dir.Append(Function(DirectoryItem(gettalks, "Rated jaw-dropping"), pageUrl = jawdrop))
    dir.Append(Function(DirectoryItem(gettalks, "... persuasive"), pageUrl = persu))
    dir.Append(Function(DirectoryItem(gettalks, "... ingenious"), pageUrl = ingen))
    dir.Append(Function(DirectoryItem(gettalks, "... fascinating"), pageUrl = fasc))
    dir.Append(Function(DirectoryItem(gettalks, "... inspiring"), pageUrl = inspi))
    dir.Append(Function(DirectoryItem(gettalks, "... beautiful"), pageUrl = beaut))
    dir.Append(Function(DirectoryItem(gettalks, "... funny"), pageUrl = funny))
    dir.Append(Function(DirectoryItem(gettalks, "... informative"), pageUrl = infor))
    
    return dir

####################################################################################################

def ThemeList(sender,pageUrl):
   
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")

    
    content = HTML.ElementFromURL(pageUrl)
    page=HTTP.Request(pageUrl)

    
    for themes in content.xpath('//div[@id="maincontent"]/div/div/div/ul/li/a'):
        themeid=themes.get('href')
        themeid=themeid.replace('/talks/tags/id/','')
        themename=themes.text
        themeUrl="http://www.ted.com" + themeid
        link=HTML.ElementFromURL(themeUrl).xpath('//link[@rel="alternate"]')[0].get('href')
        dir.Append(Function(DirectoryItem(ThemeSort, title=themename), pageUrl = link))
    
    return dir

####################################################################################################

def ThemeSort(sender,pageUrl):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")
    
    content=XML.ElementFromURL(pageUrl)
    
    for item in content.xpath("/rss/channel/item"):
        links=item.xpath("//link")
        titles=item.xpath("//title")
        pubdates=item.xpath("//pubDate")
        descs=item.xpath("//description")
        
    count=-1
    for link in links:
        count=count+1
        Log(count)
        if count >1:
            vidUrl=links[count].text
            vidtitle=titles[count].text
            viddate=pubdates[count-2].text
            viddesc=descs[count-2].text

            
            content=HTML.ElementFromURL(vidUrl).xpath('//dl[@class="downloads"]')[1]            
            for items in content:
                #if audio is available
                vidUrl2=content.xpath('//dt')[3]


        
            link=vidUrl2.xpath("a")[0].get('href')
            trueUrl="http://www.ted.com" + link + "#.mp4"
            thumb=HTML.ElementFromURL(vidUrl).xpath('//link[@rel="image_src"]')[0].get('href')

            dir.Append(VideoItem((trueUrl), title=vidtitle,subtitle=viddate, thumb=thumb, summary=viddesc))

    return dir    
####################################################################################################

def TagsList(sender,pageUrl):
    
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")
    
    content = HTML.ElementFromURL(pageUrl)
    page=HTTP.Request(pageUrl)

    
    for tags in content.xpath('//div[@id="maincontent"]/div/div/div/ul/li/a'):
        tagid=tags.get('href')
        tagid=tagid.replace('/talks/tags/id/','')
        tagname=tags.text
        jsonUrl="http://www.ted.com/talks/searchRpc?tagid=" + tagid + "&orderedby=NEWEST"
        
        dir.Append(Function(DirectoryItem(gettalks, title=tagname), pageUrl = jsonUrl))
        
    return dir

####################################################################################################    
        
def gettalks(sender,pageUrl):       
     dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")   
     jsontag=JSON.ObjectFromURL(pageUrl)['main']

     for talks in jsontag:
         id=talks['id']
         talkDate=talks['talkDate']
         talkfDate=talks['talkfDate']
         talkcDate=talks['talkcDate']
         talkpDate=talks['talkpDate']
         talkDuration=talks['talkDuration']
         talkLink=talks['talkLink']
         talkLink="http://www.ted.com" + talkLink
         
         content=HTML.ElementFromURL(talkLink).xpath('//dl[@class="downloads"]')[1]            
         for items in content:
             #if audio is available
             vidUrl2=content.xpath("dt")[2]
             

            
        
         link=vidUrl2.xpath("a")[0].get('href')
         trueUrl="http://www.ted.com" + link + "#.mp4"
         link=trueUrl



         tTitle=talks['tTitle']
         altTitle=talks['altTitle']
         blurb=talks['blurb']
         blurb=blurb.replace("&#39;","'")
         speaker=talks['speaker']
         fName=talks['fName']
         lName=talks['lName']
            
         talkratings=talks['ratings']
         ratingname=[]
         ratingid=[]
         for ratings in talkratings:
             ratingname.append(ratings['name'])
             ratingid.append(ratings['id'])
            
         image=talks['image']
         thumb="http://images.ted.com/images/ted/" + str(image) + "_240x180.jpg"

         title2=talkDate + " (" + talkDuration + ")"
         dir.Append(VideoItem(link, title=altTitle,subtitle=title2, thumb=thumb, summary=blurb))
         
     return dir
            
        
    
    
    
    
    
    
    
    
    
    
    
    
    