import json
import time
from requests_oauthlib import OAuth1Session
from flask import Flask, redirect, request
from flask.helpers import get_root_path
import tweepy
import pyodbc
from random import randint, uniform,random
####Activate virtualenv venv\Scripts\activate
direccion_servidor = '45.169.100.7'
nombre_bd = 'sanjusto_twitterapp'
nombre_usuario = 'sanjusto_sanjusto'
password = 'sz2dKOe&Y9~J35'


##API VIEJA
#consumer_key = 'BlpYFNSbQKJQIyGQJJYOMWu6C'
#consumer_secret = 'JihAZDWdZ5I0ggij5JxdzprRvXgD3G2jomc802HKr5unUCFcxv'
##API NUEVAs
consumer_key = 'AqC10PeMiDZfW1UmqhYFg8QgX'
consumer_secret = 'wg3R098YrmWqvRJZJgc8j2DH5oUQGws9hFFniWkUNhXvp1yOEt'
resource_owner_key = ''
resource_owner_secret = ''

access_token = ''
access_token_secret = ''

#se setean en la funcion verificacion completa, pero al pasar a main no estan mas.. revisar

app = Flask(__name__)

@app.route('/main')
def funcionDesencadenadora(api): #En esta funcion puedo hacer todo lo que TweetPy me permita con la cuenta que se autorice
    data = api.get_user("nike")
    id_ultimo_tweet = data._json["status"]["id"]
    api.create_favorite(id_ultimo_tweet)
    return "se completo el retweet  asdasd"
   # auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   # print("ESTE ES EL ACCESSTOKEN Y EL SECRET: "+access_token+"   Y   " + access_token_secret )
   # auth.set_access_token(access_token, access_token_secret)
   # api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def guardarDatosAccesoUsuario(conn,accesstoken,accesstokensecret,userName,userId):
    cursor = conn.cursor()
    query = ("INSERT INTO sanjusto_sanjusto.accessaccount (accesstoken, accesstokensecret,userid,username) VALUES(?,?,?,?)")
    values = [accesstoken,accesstokensecret,userId,userName]
    cursor.execute(query,values)
    conn.commit()
    conn.close()

def guardarDatosAccesoUsuario2(conn,accesstoken,accesstokensecret,userName,userId):
    cursor = conn.cursor()
    query = ("INSERT INTO sanjusto_sanjusto.accessaccount2 (accesstoken, accesstokensecret,userid,username) VALUES(?,?,?,?)")
    values = [accesstoken,accesstokensecret,userId,userName]
    cursor.execute(query,values)
    conn.commit()
    conn.close()

#Esta funcion recibe los parametros necesarios para devolver la API abierta en la cual se pueda hacer todo con una cuenta.
def getControlUsuario(consumerKey,consumerSecret,accessToken,accessTokenSecret):
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

def insertarEnBdd(conn,userData):
    cursor = conn.cursor()
    query = ("UPDATE sanjusto_sanjusto.accessaccount SET username=?,userid=?,lastTweet=?")
    values = [userData[1],userData[0],userData[2]]
    cursor.execute(query,values)
    conn.commit()
    conn.close()

def obtenerDatosUsuario(api):
    data = api.me()
    print( json.dumps(data._json, indent=2))
    datosTupla = data.id,data.screen_name,data.status.id
    print(datosTupla)
    return datosTupla


def buscarUsuarioEnBddConAccessToken(conn,accessToken,accessTokenSecret):
    cursor = conn.cursor()
    query = ("SELECT * FROM sanjusto_sanjusto.accessaccount WHERE accesstoken=? and accesstokensecret=?")
    values = [accessToken,accessTokenSecret]
    cont = 0
    for row in cursor.execute(query,values):
        cont += 1
    print(cont)
    conn.commit()
    conn.close()
    return cont

def buscarUsuarioEnBddConAccessToken2(conn,accessToken,accessTokenSecret):
    cursor = conn.cursor()
    query = ("SELECT * FROM sanjusto_sanjusto.accessaccount2 WHERE accesstoken=? and accesstokensecret=?")
    values = [accessToken,accessTokenSecret]
    cont = 0
    for row in cursor.execute(query,values):
        cont += 1
    print(cont)
    conn.commit()
    conn.close()
    return cont

def getTwitterPadreBdd(conn,api,userId):
    cursor = conn.cursor()
    query = ("SELECT twitterPadre FROM sanjusto_sanjusto.accessaccount WHERE userId=?")
    values = [userId]
    for row in cursor.execute(query,values):
        twitterPadreName = row.twitterPadre
    conn.commit()
    conn.close()
    print(twitterPadreName)
    return twitterPadreName


def getRetweetIdPadre(api,twitterPadreUser):
    data = api.get_user(twitterPadreUser)
    print('Es retweet' if hasattr(data.status,'retweeted_status') else 'NOP')
   # print(json.dumps(data.status._json, indent=2))
    if hasattr(data.status,'retweeted_status'):
        return data.status.retweeted_status.id
    return ''

def postRetweet(api,retweetId):
    api.retweet(retweetId)

def loopRetweet(api,userId):#Es un loop en el cual esta constantemente comprobando si hay un nuevo retweet de la cuenta padre para replicar
    mins = 0
    twitterPadreUser = getTwitterPadreBdd(connectToSql(),api,userId)
    lastRetweetId = ''
    while mins != 10000:
        print(">>>>>>>>>>>>>>>>>>>>> {}".format(mins))
        # Sleep for a minute --> comprueba cada 1 minuto si hay un nuevo tweet que retweetear
        time.sleep(5)
        retweetId = getRetweetIdPadre(api,twitterPadreUser)
        if retweetId != lastRetweetId and retweetId != '':
            postRetweet(api,retweetId)
            lastRetweetId = retweetId
        mins += 1

def guardarRetweetIdBdd(conn,retweetId):
    cursor = conn.cursor()
    query = ("INSERT INTO sanjusto_sanjusto.homeLineRetweets (retweetId) VALUES (?)")
    values = [retweetId]

    try:
        cursor.execute(query,values)
    except:
        print("El id del retweet ya esta repetido.....")
    conn.commit()


def buscarTweetsHomeLine(api):
    # fetching the statuses
    statuses = api.home_timeline(count= 200)
 #   print(json.dumps(statuses._json, indent=2))
    print(len(statuses))
    # printing the screen names of each status
    i = 0
    conn = connectToSql()
    for status in statuses:
        if hasattr(status,'retweeted_status'):
            print("se encontro un retweet")
            i+=1
            guardarRetweetIdBdd(conn,status.id)

    conn.close()
    return i

def retweetearHomeLineBdd(api,conn):
    cursor = conn.cursor()
    query = ("SELECT retweetId FROM sanjusto_sanjusto.homeLineRetweets")
    for row in cursor.execute(query):
        try:
            api.retweet(row.retweetId)
            time.sleep(20)
        except:
             print("Fallo al retweetear")

    conn.commit()
    conn.close()
    return "Se completaron los rtweets"

def guardarCuentaIdBdd(conn,userId):
    cursor = conn.cursor()
    query = ("INSERT INTO sanjusto_sanjusto.accountsToFollow (userId) VALUES (?)")
    values = [userId]

    try:
        cursor.execute(query,values)
    except:
        print("El id del retweet ya esta repetido.....")
    conn.commit()

def obtenerFollowersDeCuenta(api,twitterNombre):
    conn = connectToSql()
    for user in tweepy.Cursor(api.followers, screen_name=twitterNombre).items(200):
        guardarCuentaIdBdd(conn,user.id)

def obtenerIdUsuariosEspecificados(listCuentas,api):
    conn = connectToSql()
    for user in listCuentas:
        data = api.get_user(user)
        guardarCuentaIdBdd(conn, data.id)


def seguirCuentasEspecificadas(listCuentas):
    listApis = []
    conn = connectToSql()
    cursor = conn.cursor()
    query = ("SELECT accesstoken,accesstokensecret FROM sanjusto_sanjusto.accessaccount")
    # Genero la lista de todas las API para manejar todas las cuentas de mi base de datos:
    for access in cursor.execute(query):
        listApis.append(getControlUsuario(consumer_key, consumer_secret, access.accesstoken, access.accesstokensecret))

    conn.commit()
    conn.close()
    currentCantSeguidos = 0
    print("cantidad de apis " + str(len(listApis)))
    print("cantidad de users " + str(len(listCuentas)))
    print("cantidad de seguimientos a realizar " + str(len(listApis) * len(listCuentas)))
    contErrores = 0
    while currentCantSeguidos < len(listApis) * len(listCuentas) - 500:
        numCuentaRandom = randint(0, len(listCuentas) - 1)
        numApiRandom = randint(0, len(listApis) - 1)
        print("numero de api: " + str(numApiRandom))
        try:
             listApis[numApiRandom].create_friendship(listCuentas[numCuentaRandom])
             currentCantSeguidos += 1
             print(str(currentCantSeguidos) + " API: " + str(numApiRandom))
             time.sleep(50)
             contErrores = 0
        except Exception as e:
            print("La API " + str(numApiRandom) + str(e))
            contErrores += 1
            if contErrores == 30:
                currentCantSeguidos = 1000000

    if currentCantSeguidos == 1000000:
         return "Se termino con error"
    else:
        return "Se termino de seguir a las cuentas especificadas"

def guardarCuentaBloqueada(indexCuenta):
    listCuentas = []
    conn = connectToSql()
    cursor = conn.cursor()
    query = ("SELECT username,numCel FROM sanjusto_sanjusto.accessaccount")
    for user in cursor.execute(query):
        listCuentas.append(user)

    query2 = ("INSERT INTO sanjusto_sanjusto.cuentasbloqueadas VALUES(?,?)")
    values = [listCuentas[indexCuenta].username,listCuentas[indexCuenta].numCel]
    try:
        cursor.execute(query2, values)
    except:
        print()
    conn.commit()
    conn.close()

@app.route('/followAccounts')
def seguirCuentas():
    listApis = []
    listUsers = []
    conn = connectToSql()
    cursor = conn.cursor()
    query = ("SELECT accesstoken,accesstokensecret FROM sanjusto_sanjusto.accessaccount")
    # Genero la lista de todas las API para manejar todas las cuentas de mi base de datos:
    for access in cursor.execute(query):
        listApis.append(getControlUsuario(consumer_key, consumer_secret, access.accesstoken, access.accesstokensecret))

    query2 = ("SELECT userId FROM sanjusto_sanjusto.accountsToFollow")
    # Genero la lista de usuarios que debo seguir
    for user in cursor.execute(query2):
        listUsers.append(user.userId)

    conn.commit()
    conn.close()
    currentCantSeguidos = 0
    print("cantidad de apis " + str(len(listApis)))
    print("cantidad de users " + str(len(listUsers)))
    print("cantidad de seguimientos a realizar " + str(len(listApis) * len(listUsers)))
    contErrores = 0
    while currentCantSeguidos < len(listApis) * len(listUsers)*5:
        numCuentaRandom = randint(0, len(listUsers) - 1)
        numApiRandom = randint(0, len(listApis) - 1)
        try:
             listApis[numApiRandom].create_friendship(listUsers[numCuentaRandom])
             currentCantSeguidos += 1
             print(str(currentCantSeguidos) + " API: " + str(numApiRandom) + " Siguio a la cuenta: " +listUsers[numCuentaRandom])
             time.sleep(60)
             contErrores = 0
        except Exception as e:
            print("La API " + str(numApiRandom) + str(e))
            if e.args[0][0]['code'] == 326:
                guardarCuentaBloqueada(numApiRandom)
                #listApis.pop(numApiRandom)

            #if e.args[0][0]['code'] == 226:
                #listApis.pop(numApiRandom)

            contErrores += 1
            if contErrores == 30:
                currentCantSeguidos = 1000000
                #time.sleep(500)
                #redirect("http://127.0.0.1:5000/retweetear", code=302)

    #return redirect("http://127.0.0.1:5000/retweetear", code=302)
    return "Se termino de seguir las cuentas"

@app.route('/likear')
def likear():
    listApis = []
    listTweets = []
    conn = connectToSql()
    cursor = conn.cursor()
    query = ("SELECT accesstoken,accesstokensecret FROM sanjusto_sanjusto.accessaccount")
    #Genero la lista de todas las API para manejar todas las cuentas de mi base de datos:
    for access in cursor.execute(query):
        listApis.append(getControlUsuario(consumer_key,consumer_secret,access.accesstoken,access.accesstokensecret))

    query2 = ("SELECT retweetId FROM sanjusto_sanjusto.homeLineRetweets")
    #Genero la lista de usuarios que debo seguir
    for retweet in cursor.execute(query2):
        listTweets.append(retweet.retweetId)

    conn.commit()
    conn.close()
    currentCantSeguidos = 0
    print("cantidad de apis "+str(len(listApis)))
    print("cantidad de users " + str(len(listTweets)))
    print("cantidad de retweets a realizar " + str(len(listApis)*len(listTweets)))
    contErrores = 0
    while currentCantSeguidos < len(listApis)*len(listTweets)*3:
        numTweetRandom = randint(0,len(listTweets)-1)
        numApiRandom = randint(0,len(listApis)-1)
        try:
          listApis[numApiRandom].create_favorite(listTweets[numTweetRandom])
          currentCantSeguidos += 1
          print("Se dio un like")
          time.sleep(20)
          contErrores = 0
        except Exception as e:
          print("La API " + str(numApiRandom) + str(e))
          if e.args[0][0]['code'] == 326:
              guardarCuentaBloqueada(numApiRandom)
              #listApis.pop(numApiRandom)

          #if e.args[0][0]['code'] == 226:
              #listApis.pop(numApiRandom)

          contErrores += 1
          if contErrores == 50:
              currentCantSeguidos = 1000000

    return "Se terminaron de retweetear"

@app.route('/retweetear')
def retweetear():
    listApis = []
    listTweets = []
    conn = connectToSql()
    cursor = conn.cursor()
    query = ("SELECT accesstoken,accesstokensecret FROM sanjusto_sanjusto.accessaccount")
    #Genero la lista de todas las API para manejar todas las cuentas de mi base de datos:
    for access in cursor.execute(query):
        listApis.append(getControlUsuario(consumer_key,consumer_secret,access.accesstoken,access.accesstokensecret))

    query2 = ("SELECT retweetId FROM sanjusto_sanjusto.homeLineRetweets")
    #Genero la lista de usuarios que debo seguir
    for retweet in cursor.execute(query2):
        listTweets.append(retweet.retweetId)

    conn.commit()
    conn.close()
    currentCantSeguidos = 0
    print("cantidad de apis "+str(len(listApis)))
    print("cantidad de users " + str(len(listTweets)))
    print("cantidad de retweets a realizar " + str(len(listApis)*len(listTweets)))
    contErrores = 0
    while currentCantSeguidos < len(listApis)*len(listTweets)*5:
        numTweetRandom = randint(0,len(listTweets)-1)
        numApiRandom = randint(0,len(listApis)-1)
        try:
         listApis[numApiRandom].retweet(listTweets[numTweetRandom])
         currentCantSeguidos += 1
         print(str(currentCantSeguidos) + " API: " + str(numApiRandom))
         time.sleep(120)
         contErrores = 0
        except Exception as e:
            print("La API "+ str(numApiRandom)+ str(e))
            if e.args[0][0]['code'] == 326:
                guardarCuentaBloqueada(numApiRandom)
                #listApis.pop(numApiRandom)

            #if e.args[0][0]['code'] == 226:
                #listApis.pop(numApiRandom)

            contErrores += 1
            if contErrores == 50:
                currentCantSeguidos = 1000000
                #time.sleep(500)
                #redirect("http://127.0.0.1:5000/followAccounts", code=302)

    #return redirect("http://127.0.0.1:5000/followAccounts", code=302)
    return "se termino de retweetear"

@app.route('/retweetearNuevo')
def retweetearNuevo():
    listApis = []
    listTweets = []
    conn = connectToSql()
    cursor = conn.cursor()
    query = ("SELECT accesstoken,accesstokensecret FROM sanjusto_sanjusto.accessaccount")
    #Genero la lista de todas las API para manejar todas las cuentas de mi base de datos:
    for access in cursor.execute(query):
        listApis.append(getControlUsuario(consumer_key,consumer_secret,access.accesstoken,access.accesstokensecret))

    query2 = ("SELECT retweetId FROM sanjusto_sanjusto.homeLineRetweets")
    #Genero la lista de usuarios que debo seguir
    for retweet in cursor.execute(query2):
        listTweets.append(retweet.retweetId)

    conn.commit()
    conn.close()
    currentCantSeguidos = 0
    print("cantidad de apis "+str(len(listApis)))
    print("cantidad de users " + str(len(listTweets)))
    print("cantidad de retweets a realizar " + str(len(listApis)*len(listTweets)))
    contErrores = 0
    while currentCantSeguidos < len(listApis)*len(listTweets)*5:
        contErrores = 0
        i = 0
        for api in listApis:
            numTweetRandom = randint(0, len(listTweets) - 1)
            try:
                api.retweet(listTweets[numTweetRandom])
                currentCantSeguidos += 1
                print("La API " + str(i) + "hizo el retweet")
            except Exception as e:
                print("La API " + str(i) + str(e))
                if e.args[0][0]['code'] == 326:
                    guardarCuentaBloqueada(i)
                contErrores += 1
                if contErrores == len(listApis)-1:
                    currentCantSeguidos = 100000000
            i += 1
        print("Retweets totales realizados: " + str(currentCantSeguidos) +" esperando para proseguir...")
        time.sleep(700)

    time.sleep(2500)

    return redirect("http://127.0.0.1:5000/retweetearNuevo", code=302)
    #return "se termino de retweetear"

@app.route('/empezar')
def hello_world():
    data = twitter_get_oauth_request_token()
    print("primero: " + data[0] + " segundo: " + data[1] )
    return get_oauth_verifier(data)




@app.route('/verificacion')
def verificacion_completa():
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    accessTokenList = twitter_get_access_token(oauth_verifier,resource_owner_key,resource_owner_secret)
#ahora parto el accessTokenList para obtener el access_token_key y access_token_secret
    access_token_key = str.split(accessTokenList[0], '=')
    access_token_secr = str.split(accessTokenList[1], '=')
    access_token_name = str.split(accessTokenList[3], '=')
    access_token_id = str.split(accessTokenList[2], '=')
    access_token = access_token_key[1]
    access_token_secret = access_token_secr[1]
    userName = access_token_name[1]
    userId = access_token_id[1]
    ## Al acceder por primera vez con una cuenta, me guarda los datos de la cuenta en la base de datos:
    if buscarUsuarioEnBddConAccessToken(connectToSql(),access_token,access_token_secret) == 0:
        guardarDatosAccesoUsuario(connectToSql(),access_token,access_token_secret,userName,userId) #Esta funcion se debe realizar una vez por usuario.
    ##getControlUsuario me proporciona la api con los permisos para hacer todo con una determinada cuenta
    api = getControlUsuario(consumer_key,consumer_secret,access_token,access_token_secret)
    ############# DESDE ACA DEBO DERIVAR A REALIZAR LAS ACCIONES QUE QUIERA HACER CON LA CUENTA
    #loopRetweet(api,userId)
    #return "good"

    #listCuentas = ['MrBeastYT','CRYPTOFIED1','ccomissioner','DorianCrypto','RealAlexCorral','CryptoDyudester','CryptoMarketHub','notEezzy','zeusyeet2']
    #obtenerIdUsuariosEspecificados(listCuentas,api)
    ##Obtener y guardar en BDD los followers de la cuenta especificada:
    #obtenerFollowersDeCuenta(api,"LandoGriffin18")
    #return "bien"
    ##Sigue las cuentas especificadas ateriormente con todas las APIs en la BDD
    #seguirCuentas()
    #return "Se agregaron todos los followss"
    #---------------------------------------------------------------------------
    ##Buscar HomeTimeLine retweets y cargarlos a la BDD:
    return 'se encontraron: ' + str(buscarTweetsHomeLine(api)) + ' retweets'
    ##Retweetea los tweets encontrados anteriormente:
    #return retweetearHomeLineBdd(api,connectToSql())


### Obtener mi informacion
#data = api.me()
#print( json.dumps(data._json, indent=2))

### Obtener informacion de otro usuario
#data = api.get_user("nike")
#print( json.dumps(data._json, indent=2))

### Obtener los followers de un usuario
#data = api.followers(screen_name="nike")
## Mostrar 20 usuaruis por defecto
#for user in data:
#    print(json.dumps(user._json, indent=2))

## Mostrar cantidad de registros que tiene un dato
#print(len(data))

## Mostrar usuarios (o lo que sea) cantidad que se quiera utilizando Cursor
#for user in tweepy.Cursor(api.followers, screen_name="nike").items(100):
#    print(json.dumps(user._json, indent=2))

### Obtener followees de un usuario
#data = api.followers(screen_name="nike")
#for user in tweepy.Cursor(api.friends, screen_name="nike").items(100):
#  print(json.dumps(user._json, indent=2))

### Obtener time-line de un usuario
#for tweet in tweepy.Cursor(api.user_timeline,screen_name="nike", tweet_mode="extended").items(1):
#    print(json.dumps(tweet._json, indent=2))

### Buscar tweets

#for tweet in tweepy.Cursor(api.search, q="giveaway csgo", tweet_mode="extended").items(1):
## Para mostrar todo el objeto tweet
#    print(json.dumps(tweet._json, indent=2))
## Para mostrar atributos seleccionados
''' 
    print(tweet._json["full_text"])
    print(tweet._json["user"]["screen_name"])
    i = 0
    for userMention in tweet._json["entities"]["user_mentions"]:
        print(tweet._json["entities"]["user_mentions"][i])
        i = i+1
'''

### Publicar un tweet
''' 
api.update_status("...")
'''

### Retweetear
''' 
tweet_id = ' (aca va el id del tweet) '
api.retweet(tweet_id)
## Retweetear ultimo tweet de una cuenta
data = api.get_user("nike")
id_ultimo_tweet = data._json["status"]["id"]
api.retweet(id_ultimo_tweet)
'''

### Dar like ultimo tweet de una cuenta
'''
data = api.get_user("nike")
id_ultimo_tweet = data._json["status"]["id"]
api.create_favorite(id_ultimo_tweet)
## Dislike
api.destroy_favorite(id_ultimo_tweet)
'''

### Responder un tweet
'''
data = api.get_user("nike")
id_ultimo_tweet = data._json["status"]["id"]
api.update_status("...", in_reply_to_status_id=id_ultimo_tweet)
'''

### Publicar tweet con fotografia
## Primero hay que subir la foto (este comando solo se debe ejecutar una vez)
'''
data_img = api.media_upload("./foto.PNG")
'''
## Luego se publica el tweet con la/s foto/s
'''
api.update_status(media_ids=["1357155295697522689"])
'''

### Seguir una cuenta
'''
api.create_friendship("nike")
'''
### Dejar de seguir una cuenta
'''
api.destroy_friendship("nike")
'''

### Bloquear una cuenta
'''
api.create_block("nike")
'''
### Desbloquear una cuenta
'''
api.destroy_block("nike")
'''

### Enviar un mensaje privado a una cuenta
## Primero necesitamos el id del usuario
'''
data = api.get_user("nike")
id_usuario = data._json["id"]
'''
## Luego el comando para enviar el mensaje
'''
api.send_direct_message(id_usuario, text="Hello")
'''



def twitter_get_oauth_request_token():
    global resource_owner_key
    global resource_owner_secret
    request_token = OAuth1Session(client_key=consumer_key, client_secret=consumer_secret)
    url = 'https://api.twitter.com/oauth/request_token'
    data = request_token.get(url)
    print(data.text)
    data_token = str.split(data.text, '&')
    ro_key = str.split(data_token[0], '=')
    ro_secret = str.split(data_token[1], '=')
    resource_owner_key = ro_key[1]
    resource_owner_secret = ro_secret[1]
    resource = [resource_owner_key, resource_owner_secret]
    return resource

def get_oauth_verifier(resource):
    return redirect("https://api.twitter.com/oauth/authenticate?oauth_token="+resource[0], code=302)

def twitter_get_access_token(verifier, ro_key, ro_secret):
    oauth_token = OAuth1Session(client_key=consumer_key,
                                client_secret=consumer_secret,
                                resource_owner_key=ro_key,
                                resource_owner_secret=ro_secret)
    url = 'https://api.twitter.com/oauth/access_token'
    data = {"oauth_verifier": verifier}
    print(ro_key)
    print(ro_secret)
    access_token_data = oauth_token.post(url, data=data)
    print(access_token_data.text)
    access_token_list = str.split(access_token_data.text, '&')
    return access_token_list


def twitter_get_user_data(access_token_list):
    access_token_key = str.split(access_token_list[0], '=')
    access_token_secret = str.split(access_token_list[1], '=')
    access_token_name = str.split(access_token_list[3], '=')
    access_token_id = str.split(access_token_list[2], '=')
    key = access_token_key[1]
    secret = access_token_secret[1]
    name = access_token_name[1]
    id = access_token_id[1]
    oauth_user = OAuth1Session(client_key=consumer_key,
                               client_secret=consumer_secret,
                               resource_owner_key=key,
                               resource_owner_secret=secret)
    url_user = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    params = {"include_email": 'true'}
    user_data = oauth_user.get(url_user, params=params)
    print(user_data.json())
    return user_data.json()


@app.route('/connectToSql')
def connectToSql():
    try:
        conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                                  direccion_servidor+';DATABASE='+nombre_bd+';UID='+nombre_usuario+';PWD=' + password)
        # OK! conexión exitosa
        return conexion
    except Exception as e:
        # Atrapar error
        print("Ocurrió un error al conectar a SQL Server: ", e)
        return None






### LISTO YA TENGO ACCESO A TODA LA CUENTA QUE ME DE AUTORIZACION