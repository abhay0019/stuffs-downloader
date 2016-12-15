#!/usr/bin/python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from threading import Thread
import re
import sys
import time
import copy
import os
import commands
import shutil
import subprocess as s
download_dir=''
series=''
season=''
episode=''
def DOM_to_innerHTML(elements):
  vect=[]
  for element in elements:
    match=element.get_attribute('innerHTML')
    vect.append(match)
    #print match
  return vect

def Name_to_list(name):
  return name.split(' ')
  
def maxmatch(names,eles):
  mx=0
  for i in range(0,len(eles)):
    cnt=0
    eles[i]=eles[i][:-1]
    vect=eles[i].split(' ')
    for w in names:
      for word in vect:                                #Compare word with w
        if w==word:
          cnt=cnt+1
          break
    if mx<cnt:
      mx=cnt
            
  return mx
        
def best_match(names,elements):
  eles=((':'.join(elements)).lower()).split(':')
  index_vect=[]
  mx=maxmatch(names,eles)
  if mx==0:
    return index_vect
  else:
    for i in range(0,len(eles)):
      cnt=0
      vect=eles[i].split(' ')
      for w in names:
        for word in vect:                                        #Compare word with w  
          if w==word:
            cnt=cnt+1
            break    
      if cnt==mx:
        index_vect.append(i)
  return index_vect

def final_click_specific(driver,elements,choice):
  ind=-1
  for i in range(0,len(elements)):
    gp=re.search(choice,elements[i].get_attribute('innerHTML'))
    if gp:
      ind=i
      break
  if ind!=-1:
    return elements[ind]
  else:
    print "Sorry .. Episode Not Available .."
    sys.exit()
      
def episode_choice(driver):
  print "Want to see List of Episodes and choose one of them ?(y/n)"
  check=raw_input()
  if check.lower()=='y':
    vect=driver.find_elements_by_xpath('//tr/td/a')
    show_list(driver,vect)
    ind=raw_input()
    ind=int(ind)
    return vect[ind]
  elif check.lower()=='n':  
    episode=raw_input('Enter Episode Number\n')
    episode=int(episode) 
    try:
      choice='E'
      if episode in range(1,10):
        choice+='0'+str(episode)
      else:
        choice+=str(episode)
      elements=driver.find_elements_by_xpath("//tr/td/a")
      return final_click_specific(driver,elements,choice)
    except NoSuchElementException:
      print "Episode Not Present .."
      sys.exit()
  else:
    return None    
    
def show_list(driver,vect):
  print "Choose : -"
  for i in range(1,len(vect)):
    print i,")",vect[i].get_attribute('innerHTML')
def get_username():
  s,o=commands.getstatusoutput("whoami")
  return o                        
def season_choice(driver):
  global season
  print "Want to see List of Seasons and choose one of them ?(y/n)"
  check=raw_input()
  if check.lower()=='y':
    vect=driver.find_elements_by_xpath('//tr/td/a')
    show_list(driver,vect)
    ind=raw_input()
    ind=int(ind)
    season=vect[ind].get_attribute('innerHTML')
    season=season[:-1]
    return vect[ind]
  elif check.lower()=='n':
    season=raw_input('Enter Season Number\n')
    season=int(season)
    choice='s'+str(season)+'/'
    try: 
      element=driver.find_element_by_xpath("//a[@href='"+choice+"']")
      season=choice[:-1]
      return element
    except NoSuchElementException:
      print "Season Not Present .."
      sys.exit()
  return None
def check_existence_and_wait(downloadpath,filename):
  if os.path.isdir(downloadpath):
    full_path=os.path.join(downloadpath,filename)
    while not os.path.isfile(full_path):
      time.sleep(5)
    return  
  else:
    print "Download Directory not Present .."
    sys.exit()  
       
def episode(element,driver):
  element.click()
  element=season_choice(driver)
  if element:
    element.click()
  else:
    print "Wrong Choice .."
    sys.exit()    
  vect=driver.find_elements_by_xpath('//tr/td/a')
  if vect[1].get_attribute('innerHTML')=='720p/':
    print "Available in 720p..\nWant it in 720p?(y/n)"
    check=raw_input()
    if check.lower()=='y':
      vect[1].click()
      element=episode_choice(driver)
    else:
      element=episode_choice(driver)
  else:
    element=episode_choice(driver)
  if element:
    filename=element.get_attribute('innerHTML')
    s.call(['notify-send','Downloading .. ',filename])
    element.click()
    print "Download Started .."
  else:  
    print "Wrong Choice .."
    sys.exit()
  user=get_username()  
  thread=Thread(target=check_existence_and_wait,args=("/home/"+user+"/Downloads",filename))
  thread.start()
  thread.join()
  src="/home/"+user+"/Downloads/"+filename
  global download_dir
  print "finally..",download_dir
  dest=download_dir+"/"+filename
  print "moving from",src," to ",dest 
  shutil.move(src,dest)
  print "Downloaded .."
  s.call(['notify-send','Downloaded',filename])
  driver.close()
        
def get_episode(driver,vect,episode_no):
  if episode_no in range(0,10):
    choice='E0'+str(episode_no)
  else:
    choice='E'+str(episode_no)
  for i in range(0,len(vect)):
    gp=re.search(choice,vect[i].get_attribute('innerHTML'))
    if gp:
      return vect[i]
  return None
  
def episode_list_click(driver,vect,v):
  global download_dir
  threads=[]
  filenames=[]
  user=get_username()
  for i in range(int(v[0]),int(v[1])+1):
    element=get_episode(driver,vect,i)
    if element:
      filename=element.get_attribute('innerHTML')
      s.call(['notify-send','Downloading .. ',filename])
      element.click()
      filenames.append(filename)
      thread=Thread(target=check_existence_and_wait,args=("/home/"+user+"/Downloads",filename))
      thread.start()
      threads.append(thread)
    else:
      s.call(['notify-send','Error ..',"Episode "+str(i)+" not Present"])
      print "Episode",i,"not Present"
  for i in range(0,len(threads)):
    threads[i].join()
    
  for filename in filenames:
    src="/home/"+user+"/Downloads/"+filename
    dest=download_dir+"/"+filename
    if os.path.isfile(src) and not os.path.isfile(dest):
      print "moving from",src," to ",dest 
      shutil.move(src,dest)
    print "Downloaded ..",filename
    s.call(['notify-send','Downloaded',filename])
            
def check720p(driver,vect):
  if vect[1].get_attribute('innerHTML')=='720p/':
    while True:
      choice=raw_input("Availabe in 720p..\nWant to download in 720p?(y,n)\n")
      if choice.lower()=='y':
        print "chose y"
        vect[1].click()
        break
      elif choice.lower()=='n':
        print "chose n"
        break
      else:
        print "Wrong Choice ..\nRe-enter"                          
            
def episode_list(element,driver):
  global download_dir
  global series
  global season
  print "Series ",series
  element.click()
  element=season_choice(driver)
  print "Season",season
  download_dir=download_dir+"/"+series+'  '+season
  if not os.path.isdir(download_dir):
    os.mkdir(download_dir,0777)
  if element:
    element.click()
  else:
    print "Wrong Choice .."
    sys.exit()      
  vect=driver.find_elements_by_xpath('//tr/td/a')
  check720p(driver,vect)
  vect=driver.find_elements_by_xpath('//tr/td/a')
  print "Want to see List of Episodes and choose list out of them ?(y/n)"
  choice=raw_input()
  if choice.lower()=='y':
    show_list(driver,vect)
    
  if choice.lower()=='y' or choice.lower()=='n':   
    print "List Choosing Format : \n X1-Y1,X2-Y2,X3-Y3 ... (for episodes X1 to Y1 , X2 to Y2 , X3 to Y3 ...) "
    ep_list=str(raw_input())
    chunks=ep_list.split(',')
    for chunk in chunks:
      v=chunk.split('-')
      episode_list_click(driver,vect,v)        
  else:
    print "Wrong Choice Brah !!"
    sys.exit()
    
def entire_season(element,driver):
  global season
  global series
  global download_dir
  element.click()
  element=season_choice(driver)
  download_dir=download_dir+'/'+series+' '+season
  if not os.path.isdir(download_dir):
    os.mkdir(download_dir)
  if element:
    element.click()
  else:
    print "Wrong Choice .."
    sys.exit()
  vect=driver.find_elements_by_xpath('//tr/td/a')
  fl=-1
  x=1  
  if vect[1].get_attribute('innerHTML')=='720p/':
    while True:
      choice=raw_input("Availabe in 720p..\nWant to download in 720p?(y,n)\n")
      if choice.lower()=='y':
        vect[1].click()
        fl=1
        break
      elif choice.lower()=='n':
        x=2
        break
      else:
        print "Wrong Choice ..\nRe-enter"
                                  
  vect=driver.find_elements_by_xpath('//tr/td/a')    
  threads=[]
  filenames=[]
  user=get_username()
  for i in range(x,len(vect)):
    element=vect[i]
    filename=element.get_attribute('innerHTML')
    s.call(['notify-send','Downloading .. ',filename])
    element.click()
    filenames.append(filename)
    thread=Thread(target=check_existence_and_wait,args=("/home/"+user+"/Downloads",filename))
    thread.start()
    threads.append(thread)
  if fl==1:
    vect[0].click()    
  for i in range(0,len(threads)):
    threads[i].join()
  user=get_username()  
  for filename in filenames:
    src="/home/"+user+"/Downloads/"+filename
    dest=download_dir+"/"+filename
    if os.path.isfile(src) and not os.path.isfile(dest):
      print "moving from",src," to ",dest 
      shutil.move(src,dest)
    print "Downloaded ..",filename
    s.call(['notify-send','Downloaded',filename])
    

def get_season(driver,season_no):
  choice='s'+str(season_no)+'/'
  try:
    element=driver.find_element_by_xpath("//a[@href='"+choice+"']")  
    return element
  except NoSuchElementException:
    return None
    
def entire_series(element,driver):
  global series
  global season
  global download_dir
  element.click()
  vect=[]
  v=driver.find_elements_by_xpath('//tr/td/a')
  if v[1].get_attribute('innerHTML')=='Subtitle':
    vect.append(v[0])
    vect.extend(v[2:])
  else:
    vect.extend(v[:])
  l=len(vect)
  v=copy.copy(vect)
  download_dir=download_dir+'/'+series
  if not os.path.isdir(download_dir):
    os.mkdir(download_dir)
        
  for i in range(1,len(vect)):
    vect=[]
    v=driver.find_elements_by_xpath('//tr/td/a')
    if v[1].get_attribute('innerHTML')=='Subtitle':
      vect.append(v[0])
      vect.extend(v[2:])
    else:
      vect.extend(v[:])
    season=vect[i].get_attribute('innerHTML')
    season=season[:-1]
 
    if not os.path.isdir(download_dir+'/'+season):
      os.mkdir(download_dir+'/'+season)
    vect[i].click()
    vect2=driver.find_elements_by_xpath('//tr/td/a')
    fl=-1
    if vect2[1].get_attribute('innerHTML')=='720p/':
      choice=raw_input("We have Season "+season+" available in 720p ..\nWant it in 720p?(y/n)\n")
      if choice.lower()=='y':
        vect2[1].click()
        x=1
        fl=1
        vect2=driver.find_elements_by_xpath('//tr/td/a')
      else:
        x=2
    else:
      x=1         
    filenames=[]
    threads=[]
    user=get_username()
    s.call(['notify-send','Starting Download of  ',"Season "+season])
    for j in range(x,len(vect2)):
      #vect2[j].click()
      element=vect2[j]
      filename=element.get_attribute('innerHTML')
      s.call(['notify-send','Downloading .. ',filename])
      element.click()
      filenames.append(filename)
      thread=Thread(target=check_existence_and_wait,args=("/home/"+user+"/Downloads",filename))
      thread.start()
      threads.append(thread)
    for j in range(0,len(threads)):
      threads[j].join()  
    for filename in filenames:
      src="/home/"+user+"/Downloads/"+filename
      dest=download_dir+"/"+season+'/'+filename
      if os.path.isfile(src) and not os.path.isfile(dest):
        print "moving from",src," to ",dest 
        shutil.move(src,dest)  
      print "Downloaded ..",filename
      s.call(['notify-send','Downloaded',filename])
    vect2[0].click()
    if fl==1:
      vect2=driver.find_elements_by_xpath('//tr/td/a')
      vect2[0].click()    

def ask_for_display():
  s,o=commands.getstatusoutput("ps")
  gp=re.search('Xvfb',o)
  if not gp:
    os.system("Xvfb :99 &")
  inp=raw_input("Want the GUI of entire browser?(y/n)")
  if inp.lower()=='y':
    os.environ['DISPLAY']=":0.0"
  elif inp=='n':
    os.environ['DISPLAY']=":99.0"
  else:
    print "Wrong Choice .. Exiting Program !! Run again to get service .."
def ask_for_proxy():
  print "..."

def ask_for_download_folder():
  global download_dir
  f=open("download.conf","r")
  path=f.read()
  gp=re.search('[^\s].*',path)
  if gp:
    path=gp.group()
  else:
    print "Not a Right Way to specify a Path ..\nSet the path to download in download.conf"
    sys.exit()  
  f.close()
  if path=='.':
    download_dir=os.getcwd()
  elif os.path.isdir(path):
    download_dir=path
  else:
    print "Given path is not a directory ..\nSet the path to download in download.conf"
    sys.exit()
        
def download_series(name):
  global season
  global series
  global episode
  ask_for_display()
  ask_for_download_folder()
  global download_dir
  ask_for_proxy()
  name=name.lower() 
  driver = webdriver.Chrome(executable_path="/home/abhay/Desktop/py/stuffs-downloader/chromedriver") 
  driver.implicitly_wait(60)
  driver.get("http://s1.bia2m.biz/Series/")
  elements=driver.find_elements_by_tag_name('a')
  #elements = driver.find_elements_by_xpath("//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'"+name+"')]")
  elements_innerHTML=DOM_to_innerHTML(elements)
  names=Name_to_list(name)
  
  best__match=best_match(names,elements_innerHTML)
  
  if len(best__match)==0:
    print "Bad Name Serach !! Try to be specific !!"
    sys.exit()
  elif len(best__match)==1:
    ind=0
    print "Single Result :",elements_innerHTML[ind]
  else:
    print "We have list of Results for your query .. Type index of the one you need "  
    for i in range(0,len(best__match)):
      print i+1,")",elements_innerHTML[best__match[i]][:-1]
    ind=raw_input()
    ind=int(ind)-1
    print "You Chose : ",elements_innerHTML[best__match[ind]][:-1]
    
  print "Should I download?(y/n)"
  check=raw_input()
  check=check.lower()
  if check=='y':
    series=elements_innerHTML[best__match[ind]][:-1]
    element=driver.find_element_by_link_text(elements_innerHTML[best__match[ind]])
    print "Please Specify :-\n1)Want Entire Series\n2)Want Entire Specific Season\n3)Want Specific Episode\n4)Want List of Episode from Specific Season\n"
    select=raw_input()
    if select=='1':
      entire_series(element,driver)
    elif select=='2':
      entire_season(element,driver)  
    elif select=='3':
      episode(element,driver)
    elif select=='4':
      episode_list(element,driver)
    else:
      print "Blurrrrr !!!"       
  else:
    print "Okay Bye !!"
    sys.exit()
  driver.close()

if __name__=='__main__':
  print "Enter the name of Series .."
  name=raw_input() 
  download_series(name)  
