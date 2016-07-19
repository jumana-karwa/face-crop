import cv2
import sys
import os
import requests
import unirest

old_face=[]

def upload(file_path):
    url = 'https://apicloud-facerect.p.mashape.com/process-file.json'
    files = {'file': open(file_path, 'rb')}
    r = requests.post(url)
    print r.status_code
    print r

def upload2(file_path):
    response = unirest.post("https://apicloud-facerect.p.mashape.com/process-file.json",
        headers={
            "X-Mashape-Key": "kFjxXB6p2MmshB1uWiGEnwAkaBaap1j7pppjsnkM8pAFMRXD8A"
        },
        params={
            "image": open(file_path, mode="r")
        }
    )
    #print dir(response)

    print response.body

    try:
         return response.body["faces"][0]["x"],response.body["faces"][0]["y"]
    except IndexError:
         return 0,0


def main(use_api=False):
    os.system("mkdir %s"%frames_dir)
    os.system("mkdir %s/frames"%frames_dir)
    os.system("mkdir %s/face_frames"%frames_dir)
    os.system("ffmpeg -i %s -r 30 -f image2 %s/frames/frame-%%07d.png"%(video,frames_dir))
    arr = os.listdir("%s/frames"%frames_dir)
    arr.sort()
    for file_name in arr:
        if use_api:
            x,y=upload2("%s/frames/%s"%(frames_dir,file_name))
            w=250
            h=250
            print 'ffmpeg -i %s/frames/%s -vf "crop=%s:%s:%s:%s" %s/face_frames/face_%s'%(frames_dir,file_name,w,h,x,y,frames_dir,file_name)
            os.system('ffmpeg -i %s/frames/%s -vf "crop=%s:%s:%s:%s" %s/face_frames/face_%s'%(frames_dir,file_name,w,h,x,y,frames_dir,file_name))            

        else:
            # Create the haar cascade
	    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            os.system("mkdir %s/face_frames"%frames_dir)
	    # Read the image
	    print '%s/%s'%(frames_dir,file_name)
            image = cv2.imread('%s/frames/%s'%(frames_dir,file_name))
	    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	    # Detect faces in the image
	    faces = faceCascade.detectMultiScale(
    	        gray,
    	        scaleFactor=1.1,
    	        minNeighbors=5,
    	        minSize=(150, 150),
    	        flags = cv2.cv.CV_HAAR_SCALE_IMAGE
 	    )
	
	    print "Found {0} faces!".format(len(faces))

            global old_face

            if not len(faces):
                faces=old_face
            else:
	        old_face=faces

            for (x,y,w,h) in faces[:1]:
                w=250
                h=250
    	        os.system('ffmpeg -i %s/frames/%s -vf "crop=%s:%s:%s:%s" %s/face_frames/face_%s'%(frames_dir,file_name,w,h,x,y,frames_dir,file_name))


    #making the video
    os.system("ffmpeg -framerate 1/24 -r 30 -i %s/face_frames/face_frame-%%07d.png -vcodec libx264 -pix_fmt yuv420p %s/final_%s"%(frames_dir,frames_dir,video))


    #adding audio
    os.system("ffmpeg -i %s %s/audio.mp3"%(video,frames_dir))

    #combining audio and video
    os.system("ffmpeg -i %s/final_%s -i %s/audio.mp3 -vcodec copy -acodec aac -strict experimental %s/compressed_%s"%(frames_dir,video,frames_dir,frames_dir,video))

    os.system("mv %s %s/"%(video,frames_dir))

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        upload2('uber1/frames/frame-0000001.png') 
    
    elif sys.argv[1] == 'api':
        video=sys.argv[2]
        frames_dir=video.split(".")[0]
        main(use_api=True)

    elif sys.argv[1] == 'local':
        video = sys.argv[2]
        frames_dir = video.split('.')[0]
        main()
