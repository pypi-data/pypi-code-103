import sanic
from functools import partial
import json
import os, sys
import aiohttp
import asyncio
import crayons
import logging
import fortnitepy
import PirxcyPinger

from fortnitepy.ext import commands

url = PirxcyPinger.get_url(platform='replit')
app = sanic.Sanic("KiyatoBot")
filename = ".device"
html = """
<!DOCTYPE html>
<html lang="en" class="h-100">

<head>
	<meta charset="utf-8">
	<meta name="description" content="The future are coming fast">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<meta name="keywords" content="kiyato">
	<meta property="og:type" content="website">
	<meta property="og:title" content="kiyato">
	<meta property="og:description" content="KiyatoBots">
	<title>kiyatobot</title>
	<meta name="description" content="The future are coming fast">
	<link rel="icon" href="icon.png" type="image/x-icon">
	<link rel="stylesheet" href="css.css">
	<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.10.0/css/all.css">
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/3.7.0/animate.css" type="text/css" />
	<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Wruczek/Bootstrap-Cookie-Alert@gh-pages/cookiealert.css">
	<script data-ad-client="ca-pub-8899997837601633" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js">

	</script>
	<link rel="stylesheet" href="https://youssefraafatnasry.github.io/portfolYOU/assets/css/style.css">
</head>

<body class="d-flex flex-column h-100">
	<div class="alert text-center cookiealert" role="alert">
		<b>Do you like cookies?</b> &#x1F36A; By using our website, you agree that we and certain third-parties may use cookies for analytics, performance and advertising purposes.
<button type="button" class="btn btn-primary btn-sm acceptcookies">I Understand</button>
</div>
<main class="flex-shrink-0 container mt-5">
<nav class="navbar navbar-expand-lg navbar-light">
<a class="navbar-brand" href="/"><h5><b>Welcome Kiyato</b></h5></a>
<button onclick="location.href='https://discord.gg/TzuAw6QeCP'" class="button" data-cf-modified-f01948e756116e48c69a07b1-="">
<p>Join The Discord</p>
</button><br><br> 
<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar" aria-controls="navbar" aria-expanded="false" aria-label="Toggle navigation">
<span class="navbar-toggler-icon"></span>
</button>
<div class="collapse navbar-collapse" id="navbar">
<div class="navbar-nav ml-auto">
<div class="dropdown-menu" aria-labelledby="dashboard_dropdown">
</div>
</li>
<a class="nav-item nav-link" href="/login">Login</a>
<a class="nav-item nav-link" style="color: blue;"><i class="fab fa-discord"></i></a>
<span id="theme-toggler" class="nav-item nav-link" role="button" onclick="toggleTheme()"></span>
</div>
</div>
</nav>
<style>
  
::-webkit-scrollbar {
  width: 0;
  height: 0;
}

:root {
  --gradient: linear-gradient(90deg, #5271ee, black, #121212, #ffffff, #5c5b5b, #00d0ff);

}

body {
  font-family: basic-sans, sans-serif;
  min-height: 100vh;
  display: flex;
  justify-content: ;
  align-items: center;
  font-size: 1.125em;
  line-height: 1.6;
  color: #333;
  background: #ddd;
  background-size: 300%;
  background-image: var(--gradient);
  animation: bg-animation 10s infinite;
}

@keyframes bg-animation {
  0% {background-position: left}
  50% {background-position: right}
  100% {background-position: left}
}

.content {
  background: white;
  width: 70vw;
  padding: 3em;
  box-shadow: 0 0 3em rgba(0,0,0,.15);
}

.title {
  margin: 0 0 .5em;
  text-transform: uppercase;
  font-weight: 900;
  font-style: italic;
  font-size: 3rem;
  color: #ee6352;
  line-height: .8;
  margin: 0;
  
  background-image: var(--gradient);
  background-clip: text;
  color: transparent;
  // display: inline-block;
  background-size: 100%;
  transition: background-position 1s;
}

.title:hover {
  background-position: right;
}

.fun {
  color: white;
}
</style>
<div id="container">
<style>    .hero {     text-align: center;     padding-top: 48px;     padding-bottom: 88px }  .hero-copy {     position: relative;     z-index: 1 }  .hero-cta {     margin-bottom: 40px }  .hero-figure {     position: relative }  .hero-figure svg {     width: 100%;     height: auto }  .hero-figure::before, .hero-figure::after {     content: '';     position: absolute;     background-repeat: no-repeat;     background-size: 100% }  .has-animations .hero-figure::before, .has-animations .hero-figure::after {     opacity: 0;     transition: opacity 2s ease }  .anime-ready .has-animations .hero-figure::before, .anime-ready .has-animations .hero-figure::after {     opacity: 1 }  .hero-figure::before {     top: -57.8%;     left: -1.3%;     width: 152.84%;     height: 178.78%;     background-image: url("../images/hero-back-illustration.svg") }  .hero-figure::after {     top: -35.6%;     left: 99.6%;     width: 57.2%;     height: 87.88%;     background-image: url("../images/hero-top-illustration.svg") }  .hero-figure-box {     position: absolute;     top: 0;     will-change: transform }  .hero-figure-box-01, .hero-figure-box-02, .hero-figure-box-03, .hero-figure-box-04, .hero-figure-box-08, .hero-figure-box-09 {     overflow: hidden }  .hero-figure-box-01::before, .hero-figure-box-02::before, .hero-figure-box-03::before, .hero-figure-box-04::before, .hero-figure-box-08::before, .hero-figure-box-09::before {     content: '';     position: absolute;     top: 0;     bottom: 0;     left: 0;     right: 0;     -webkit-transform-origin: 100% 100%;     transform-origin: 100% 100% }  .hero-figure-box-01 {     left: 103.2%;     top: 41.9%;     width: 28.03%;     height: 37.37%;     background: linear-gradient(to left top, #00BFFB, rgba(0, 191, 251, 0));     -webkit-transform: rotateZ(45deg);     transform: rotateZ(45deg) }  .hero-figure-box-01::before {     background: linear-gradient(to left, #15181D 0%, rgba(21, 24, 29, 0) 60%);     -webkit-transform: rotateZ(45deg) scale(1.5);     transform: rotateZ(45deg) scale(1.5) }  .hero-figure-box-02 {     left: 61.3%;     top: 64.1%;     width: 37.87%;     height: 50.50%;     background: linear-gradient(to left top, #0270D7, rgba(2, 112, 215, 0));     -webkit-transform: rotateZ(-45deg);     transform: rotateZ(-45deg) }  .hero-figure-box-02::before {     background: linear-gradient(to top, #15181D 0%, rgba(21, 24, 29, 0) 60%);     -webkit-transform: rotateZ(-45deg) scale(1.5);     transform: rotateZ(-45deg) scale(1.5) }  .hero-figure-box-03 {     left: 87.7%;     top: -56.8%;     width: 56.81%;     height: 75.75%;     background: linear-gradient(to left top, #00BFFB, rgba(0, 191, 251, 0)) }  .hero-figure-box-03::before {     background: linear-gradient(to left, #15181D 0%, rgba(21, 24, 29, 0) 60%);     -webkit-transform: rotateZ(45deg) scale(1.5);     transform: rotateZ(45deg) scale(1.5) }  .hero-figure-box-04 {     left: 54.9%;     top: -8%;     width: 45.45%;     height: 60.60%;     background: linear-gradient(to left top, #0270D7, rgba(2, 112, 215, 0));     -webkit-transform: rotateZ(-135deg);     transform: rotateZ(-135deg) }  .hero-figure-box-04::before {     background: linear-gradient(to top, rgba(255, 255, 255, 0.24) 0%, rgba(255, 255, 255, 0) 60%);     -webkit-transform: rotateZ(-45deg) scale(1.5);     transform: rotateZ(-45deg) scale(1.5) }  .hero-figure-box-05, .hero-figure-box-06, .hero-figure-box-07 {     background-color: #242830;     box-shadow: -20px 32px 64px rgba(0, 0, 0, 0.25) }  .hero-figure-box-05 {     left: 17.4%;     top: 13.3%;     width: 64%;     height: 73.7%;     -webkit-transform: perspective(500px) rotateY(-15deg) rotateX(8deg) rotateZ(-1deg);     transform: perspective(500px) rotateY(-15deg) rotateX(8deg) rotateZ(-1deg) }  .hero-figure-box-06 {     left: 65.5%;     top: 6.3%;     width: 30.3%;     height: 40.4%;     -webkit-transform: rotateZ(20deg);     transform: rotateZ(20deg) }  .hero-figure-box-07 {     left: 1.9%;     top: 42.4%;     width: 12.12%;     height: 16.16%;     -webkit-transform: rotateZ(20deg);     transform: rotateZ(20deg) }  .hero-figure-box-08 {     left: 27.1%;     top: 81.6%;     width: 19.51%;     height: 26.01%;     background: #0270D7;     -webkit-transform: rotateZ(-22deg);     transform: rotateZ(-22deg) }  .hero-figure-box-08::before {     background: linear-gradient(to left, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.48) 100%);     -webkit-transform: rotateZ(45deg) scale(1.5);     transform: rotateZ(45deg) scale(1.5) }  .hero-figure-box-09 {     left: 42.6%;     top: -17.9%;     width: 6.63%;     height: 8.83%;     background: #00BFFB;     -webkit-transform: rotateZ(-52deg);     transform: rotateZ(-52deg) }  .hero-figure-box-09::before {     background: linear-gradient(to left, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.64) 100%);     -webkit-transform: rotateZ(45deg) scale(1.5);     transform: rotateZ(45deg) scale(1.5) }  .hero-figure-box-10 {     left: -3.8%;     top: 4.3%;     width: 3.03%;     height: 4.04%;     background: rgba(0, 191, 251, 0.32);     -webkit-transform: rotateZ(-50deg);     transform: rotateZ(-50deg) }  @media (max-width: 640px) {     .hero-cta {         max-width: 280px;         margin-left: auto;         margin-right: auto     }      .hero-cta .button {         display: flex     }      .hero-cta .button+.button {         margin-top: 16px     }      .hero-figure::after,     .hero-figure-box-03,     .hero-figure-box-04,     .hero-figure-box-09 {         display: none     } }  @media (min-width: 641px) {     .hero {         text-align: left;         padding-top: 64px;         padding-bottom: 88px     }      .hero-inner {         display: flex;         justify-content: space-between;         align-items: center     }      .hero-copy {         padding-right: 64px;         min-width: 552px;         width: 552px     }      .hero-cta {         margin: 0     }      .hero-cta .button {         min-width: 170px     }      .hero-cta .button:first-child {         margin-right: 16px     }      .hero-figure svg {         width: auto     } }  .container, .container-sm {     width: 100%;     margin: 0 auto;     padding-left: 16px;     padding-right: 16px }  @media (min-width: 481px) {      .container,     .container-sm {         padding-left: 24px;         padding-right: 24px     } }  .container {     max-width: 1128px }  .container-sm {     max-width: 848px }  .container .container-sm {     max-width: 800px;     padding-left: 0;     padding-right: 0 }  .button {     display: inline-flex;     font-size: 14px;     letter-spacing: 0px;     font-weight: 600;     line-height: 16px;     text-decoration: none !important;     text-transform: uppercase;     background-color: #242830;     color: #fff !important;     border: none;     border-radius: 2px;     cursor: pointer;     justify-content: center;     padding: 16px 32px;     height: 48px;     text-align: center;     white-space: nowrap }  .button:hover {     background: #262a33 }  .button:active {     outline: 0 }  .button::before {     border-radius: 2px }  .button-sm {     padding: 8px 24px;     height: 32px }  .button-primary {     background: #097dea;     background: linear-gradient(65deg, #0270D7 0, #0F8AFD 100%) }  .button-primary:hover {     background: #0982f4;     background: linear-gradient(65deg, #0275e1 0, #198ffd 100%) }  .button-block {     display: flex }  .button-block {     display: flex;     width: 100% }  @media (max-width: 640px) {     .button-wide-mobile {         width: 100%;         max-width: 280px     } }  img {     height: auto;     max-width: 100%;     vertical-align: middle }  .feature-inner {     height: 100% }    .features-wrap {     display: flex;     flex-wrap: wrap;     justify-content: space-evenly;     margin-right: -32px;     margin-left: -32px }  .features-wrap:first-of-type {     margin-top: -16px }  .features-wrap:last-of-type {     margin-bottom: -16px }  .feature {     padding: 16px 32px;     width: 380px;     max-width: 380px;     flex-grow: 1 }    .feature-icon {     display: flex;     justify-content: center }  @media (min-width: 641px) {     .features-wrap:first-of-type {         margin-top: -24px     }      .features-wrap:last-of-type {         margin-bottom: -24px     }      .feature {         padding: 32px 32px     } }  </style>
<div id="container">
<section class="hero">
<div class="container">
<div class="hero-inner">
<div class="hero-copy">
<script src="script.js" type="ae1a82ef863b5e3683c5d35f-text/javascript"></script>
<html>
   <head>
    <style>
      @font-face { font-family: JuneBug; src: url('BurbankBigCondensed-Black.otf'); } 
      h1 {
         font-family: JuneBug
      }
    </style>
   </head>
   <body>
      <h1 style="font-size:15vw;color:white">{{friends}}/1000 Friends</h1>
   </body>
</html>
<section class="features section">
<div class="container">
<div class="features-inner section-inner has-bottom-divider">
<div class="features-wrap">
<div class="feature text-center is-revealing">
<div class="feature-inner">
<div class="feature-icon">
</div>
</section>
</div>
</main>
<script src="script.js" type="ae1a82ef863b5e3683c5d35f-text/javascript"></script>
<script src="https://ajax.cloudflare.com/cdn-cgi/scripts/7089c43e/cloudflare-static/rocket-loader.min.js" data-cf-settings="ae1a82ef863b5e3683c5d35f-|49" defer=""></script></body>
<script async defer src="https://buttons.github.io/buttons.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/wow/1.1.2/wow.js"></script>
<script>
    new WOW().init();
</script>
<script>
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
</script>
</body>
</html>
"""
class web:
  async def post(url: str, data=None, headers=None, json=None):
    async with aiohttp.ClientSession() as session:
      async with session.request(
        method="POST",        
        url=url,
        data=data,
        json=json,
        headers=headers
      ) as r:
        data = await r.text()
        try:
          jsonn = await r.json()
          return jsonn
        except:
          return data
      
  async def get(url: str, data=None, headers=None, json=None):
    async with aiohttp.ClientSession() as session:
      async with session.request(
        method="GET",        
        url=url,
        data=data,
        json=json,
        headers=headers
      ) as r:
        data = await r.text()
        try:
          jsonn = await r.json()
          return jsonn
        except:
          return data

class config:
  def __init__(self, info):
    self.info = info
    self.skin=self.info.get('skin')
    self.emote=self.info.get('emote')
    self.sac=self.info.get('sac')
    self.pioche=self.info.get('pioche')
    self.msg_bnv=self.info.get('msg_bnv')
    self.status=self.info.get('status')
    self.admins=self.info.get('admins')
    self.kyt_bot=self.info.get('kyt_bot')

class device_auths:
  def __init__(self, auths):
    self.auths = auths
    self.device_id=self.auths.get('DEVICE_ID')
    self.account_id=self.auths.get('ACCOUNT_ID')
    self.secret=self.auths.get('SECRET')

async def get_config() -> config:
  info = await web.get('https://bulkyverifiablelevel.kiyattoyager.repl.co/config')
  return config(info)

async def get_items():
  try:
    main = await web.get('https://fortnite-api.com/v2/cosmetics/br/')
    items = main['data']
    file = open("items.json", "w")
    json.dump(items, file, indent=2)
    file.close()
    logger.info(green('Cached All bot Items!'))
    return
  except:
    logger.info(red('Error Getting Items You Cannot Equip New Skins!'))
    return

async def check_status():
  while True:
    info = await web.get('https://lobbybotconfiguration.pirxcy1942.repl.co/blacklist')
    if info['kiyato'] is True:
      await asyncio.sleep(60)
    else:
      sys.exit()

async def equip_member():
  config = await get_config()
  member = bot.party.me
  if member.emote == None:
    emote = config.emote
  else:
    emote = member.emote
  try:
    await bot.party.me.clear_emote()
  except:
    pass
  try:
    await member.edit_and_keep(
      partial(
        member.set_outfit, 
        asset=config.skin
      ),
      partial(
        member.set_banner, 
        icon="InfluencerBanner17", 
        color="defaultcolor22", 
        season_level=9999
      ),
      partial(
        member.set_emote, 
        asset=emote
      )
    )
    return
  except:
    pass

def read_items():
  with open('items.json') as f:
    try:
      data = json.load(f)
      return data
    except:
      logger.info(red('Error Getting Items You May Experience Errors!'))

def clear():
  os.system("cls" if "win" in sys.platform else "clear")

def get() -> device_auths:
  auths = {}
  with open(filename) as f:
    for line in f:
      if line.startswith('#') or not line.strip():
        continue
      key, value = line.strip().split('=', 1)
      auths[key] = value.replace("\"", "")
    return device_auths(auths)

def is_admin():
  async def predicate(ctx):
    config = await get_config()
    owners = [i for i in config.admins]
    return ctx.author.id in owners
  return commands.check(predicate)

def cyan(string):
  output = crayons.cyan(string)
  return str(output)

def red(string):
  output = crayons.red(string)
  return str(output)

def green(string):
  output = crayons.green(string)
  return str(output)

#logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(cyan('[KiyatoBot] [%(asctime)s] - %(message)s'))
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('Made By Pirxcy and Kiyato')
auths = get()
bot = commands.Bot(
  command_prefix="!",
  auth=fortnitepy.DeviceAuth(
    device_id=auths.device_id,
    account_id=auths.account_id,
    secret=auths.secret,
  )
)

def lenFriends():
  friends = bot.friends
  return len(friends)

@app.route('/')
async def index(request):
  html_ = html.replace("{{friends}}", lenFriends())
  return sanic.response.html(html_)

@app.route('/id')
async def index(request):
  return sanic.response.text(os.environ)

@bot.event
async def event_ready():
  clear()
  asyncio.get_event_loop().create_task(check_status())
  logger.info('Made By Pirxcy and Kiyato')
  await get_items()
  logger.info(green(f'Client Ready as {cyan(bot.user.display_name)}'))
  try:
    await app.create_server(
      host='0.0.0.0',
      port=8000,
      return_asyncio_server=True, 
      access_log=False
    )
    logger.info(green('Launched Sanic Server!'))
  except:
    logger.info(red('Error Starting Server, Expect Your Bot To Go Offline!'))
  try:
    await PirxcyPinger.post(url=url)
    logger.info(green('Uploaded URL To PirxcyPinger'))
  except PirxcyPinger.AlreadyPinging: #if url is already submitted
    pass
  except:
    logger.info(red('Error Uploading To PirxcyPinger, Expect Your Bot To Go Offline!'))
    logger.info(red('Try Restarting Your Bot, The Upload May work ¯\_(ツ)_/¯'))
  try:
    config = await get_config()
    await bot.set_presence(config.status)
    logger.info(green('Successfully Got Status From API'))
  except:
    logger.info(red('Unable To Reach The API'))

@bot.event
async def event_party_member_join(member):
  await equip_member()
  config = await get_config()
  first = config.msg_bnv
  message = first.replace("{DISPLAY_NAME}", member.display_name)
  await bot.party.send(message)

@bot.event
async def event_friend_request(request):
  await request.accept()

@bot.event
async def event_party_invite(invite):
  await invite.accept()

@bot.command()
@is_admin()
async def invite(ctx, *, member = None):
  if member == 'all':
    friends = bot.friends
    try:
      for friend in friends:
        friend = bot.get_friend(friend)
        if friend.is_online():
          await friend.invite()
      await ctx.send(f"Invited All Online Friends.")
    except:
      pass
  else:
    try:
      if member is None:
        user = await bot.fetch_profile(ctx.author.id)
        friend = bot.get_friend(user.id)
      if member is not None:
        user = await bot.fetch_profile(member)
        friend = bot.get_friend(user.id)
        await friend.invite()
        await ctx.send(f"Invited {friend.display_name}.")
    except:
        pass

@bot.command()
@is_admin()
async def leave(ctx):
  await ctx.send('Bye.')
  await bot.party.me.clear_emote()
  await bot.party.me.set_emote(asset='EID_Wave')
  await asyncio.sleep(1.5)
  await bot.party.me.leave()

@bot.command()
async def ready(ctx):
  await BaseException.party.me.set_ready(fortnitepy.ReadyState.READY)
  await ctx.send('Set to Ready!')

@bot.command()
async def unready(ctx):
  await bot.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
  await ctx.send('Set to Unready!')

@bot.command()
async def skin(ctx, *, content = None):
  try:
    cosmetics = read_items()
    if content is None:
      await ctx.send('Try !skin ikonik')    
    elif content.upper().startswith('CID_'):
      await bot.party.me.set_outfit(asset=content)
      await ctx.send(f"Equiped {content}")
    else:
      result = []
      await ctx.send('Searching...')
      for i in cosmetics:
        if content.lower() in i['name'].lower() and i['id'].startswith('CID_'):
          result.append(
            {
              'name': i['name'],
              'id': i['id']
            }
          )
          if len(result) == 11:
            break

      if result == []:
        await ctx.send('No Result Found')      

      elif len(result) == 1:
        result = sorted(result, key=lambda x:x['name'], reverse=False)
        await bot.party.me.set_outfit(asset=result[0]['id'])                    
        skinname = result[0]['name']
        await ctx.send(f"Equiped {skinname}")                
        del result[0]

      else:
        result = sorted(result, key=lambda x:x['name'], reverse=False)
        await ctx.send(
          f"Result For {content}\n"
          +
          "\n".join([f"{num}. {i}" for num, i in enumerate([f['name'] for f in result])]) 
        )
        def check(m): 
          return m.author.id == ctx.author.id
        msg = await bot.wait_for("party_message", check=check)
        await bot.party.me.set_outfit(asset=result[int(msg.content)]['id'])
        skinname = result[int(msg.content)]['name']
        await ctx.send(f'Equiped {skinname}')
        del result[int(msg.content)]
  except Exception:
    pass

@bot.command()
async def emote(ctx, *, content = None):
  try:
    cosmetics = read_items()
    if content is None:
      await ctx.send('Try !emote scenario')    
    elif content.upper().startswith('EID_'):
      await bot.party.me.clear_emote()
      await bot.party.me.set_emote(asset=content)
      await ctx.send(f"Equiped {content}")
    else:
      result = []
      await ctx.send('Searching...')
      for i in cosmetics:
        if content.lower() in i['name'].lower() and i['id'].startswith('EID_'):
          result.append(
            {
              'name': i['name'],
              'id': i['id']
            }
          )
          if len(result) == 11:
            break

      if not result:
        await ctx.send('No Result Found')
        return    

      elif len(result) == 1:
        result = sorted(result, key=lambda x:x['name'], reverse=False)
        await bot.party.me.clear_emote()
        await bot.party.me.set_emote(asset=result[0]['id'])                    
        skinname = result[0]['name']
        await ctx.send(f"Equiped {skinname}")                
        del result[0]
        return

      else:
        result = sorted(result, key=lambda x:x['name'], reverse=False)
        await ctx.send(
          f"Result For {content}\n"
          +
          "\n".join([f"{num}. {i}" for num, i in enumerate([f['name'] for f in result])]) 
        )
        def check(msg): 
          return msg.author == ctx.author
        
        msg = await bot.wait_for("party_message", check=check)   
        await bot.party.me.clear_emote()               
        await bot.party.me.set_emote(asset=result[int(msg.content)]['id'])
        skinname = result[int(msg.content)]['name']
        await ctx.send(f'Equiped {skinname}')
        del result[int(msg.content)]
        return
  except:
    pass

bot.run()