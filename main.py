import numpy
import os
import random
import schedule
import smartcrop
import time
import twitter
from PIL import Image

def bbox(img):
    rows = numpy.any(img, axis=1)
    cols = numpy.any(img, axis=0)
    rmin, rmax = numpy.where(rows)[0][[0, -1]]
    cmin, cmax = numpy.where(cols)[0][[0, -1]]

    return cmin, rmin, cmax - cmin, rmax - rmin

def pad(img, x, y):
    result = Image.new(img.mode, (1500, 500), (0, 0, 0))
    result.paste(img, (x, y))
    return result

def GenerateImage():
  sc = smartcrop.SmartCrop()

  masks = list(os.scandir("./masks"))
  images = list(os.scandir("./images"))
  images = random.sample(images, len(masks))

  result = Image.new("RGB", (1500, 500), (21, 32, 43))

  for [mask, image] in zip(masks, images):
    mask = Image.open(mask.path).convert('RGB')
    maskL = mask.convert("L")
    mask = numpy.array(mask)

    x, y, width, height = bbox(mask)

    src = Image.open(image.path).convert('RGB')

    bounds = sc.crop(src, width, height)["top_crop"]

    src = src.resize((width, height), resample=Image.LANCZOS, box=(bounds["x"], bounds["y"], bounds["width"] + bounds["x"], bounds["height"] + bounds["y"]))
    src = pad(src, x, y)

    src = numpy.array(src)
    dst = mask / 255 * src
    dst = Image.fromarray(dst.astype(numpy.uint8))
    
    result.paste(dst, (0, 0), maskL)

  timestr = time.strftime("%Y%m%d-%H%M%S")
  filename = f"./results/{timestr}_result.png"
  result.save(filename)

  api = twitter.Api(consumer_key=os.environ.get('TWITTER_API_KEY'),
                    consumer_secret=os.environ.get('TWITTER_API_SECRET'),
                    access_token_key=os.environ.get('TWITTER_ACCESS_KEY'),
                    access_token_secret=os.environ.get('TWITTER_ACCESS_SECRET'))

  api.UpdateBanner(filename)

schedule.every().sunday.at("00:00").do(GenerateImage)

while True:
    schedule.run_pending()
    time.sleep(1)
