import tweepy
import json
from time import sleep
from re import search
from itertools import cycle
from random import shuffle

# Obtener datos del archivo de configuración.
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)

screen_name = config_data["auth"]["screen_name"]

# Autorización de los valores ingresados.
auth = tweepy.OAuthHandler(config_data["auth"]["CONSUMER_KEY"], config_data["auth"]["CONSUMER_SECRET"])
auth.set_access_token(config_data["auth"]["ACCESS_TOKEN"], config_data["auth"]["ACCESS_SECRET"])
api = tweepy.API(auth)


# Preguntar al usuario qué quiere hacer y luego ejecuta la función en consecuencia
def main_menu():
    print('''

Este es un bot que te permite hacer algunas cosas:
     1. Sigue a los usuarios que te siguen.
     2. Seguir a los seguidores de otro usuario.
     3. Seguir a los usuarios en base a una palabra clave.
     4. Siga a los usuarios que retwitteó un tweet.
     5. Deja de seguir a los usuarios que no te siguen.
     6. Dejar de seguir a todos los usuarios.
     7. Me gustan los tweets basados en una palabra clave.
     8. A diferencia de todos los tweets.
     9. Envía un DM a los usuarios que te siguen.
     10. Consigue seguidor y sigue la cuenta.
     11. Salir.
    ''')

    userChoice = input('Ingrese el número de la acción que desea realizar:')

    # Diccionario de opciones del usuario.
    choices = {
        1: follow_back,
        2: follow_all,
        3: follow_keyword,
        4: follow_rters,
        5: unfollow_back,
        6: unfollow_all,
        7: fav_off_keyword,
        8: unfavorite_all,
        9: send_dm,
        10: get_count,
        11: quit
    }

    108 / 5000
    # intentar ejecutar la función de acuerdo con el número.
    # reiniciar si se le da un número o si no está en el rango.
    try:
        choices[int(userChoice)](*get_friends())
    except (ValueError, KeyError):
        print('Entrada no reconocida. Probablemente no ingresaste un número.\n'
              'El programa se reiniciará \n')
        main_menu()
    finally:
        Continue()


# función para obtener una lista de seguidores, obtiene a los usuarios de la lista blanca
def get_friends():
    # Consigue una lista de tus seguidores a seguir.
    followers = api.followers_ids(screen_name)
    following = api.friends_ids(screen_name)
    total_followed = 0

    whitelisted_users = []

    # convertir nombres de pantalla a ID de usuario

    for item in config_data["whitelisted_accounts"]:
        try:
            # Obtiene info, obtiene id.
            item = api.get_user(screen_name=item).id
            # Agrega  el id en la nueva lista
            whitelisted_users.append(item)
        except tweepy.TweepError:
            pass

    # Usuarios de la lista negra para no seguir: declarar un nombre de variable para minimizar la confusión.
    blacklisted_users = config_data["blacklisted"]

    return followers, following, total_followed, whitelisted_users, blacklisted_users


# Función para seguir a los usuarios que te siguen.
def follow_back(followers, following, total_followed, whitelisted_users, blacklisted_users):
    # Hacer lista de los que no sigue.
    non_following = set(followers) - set(following) - set(blacklisted_users)

    print('Empezando a seguir a los usuarios ...')

    # Comenzar a seguira los usuarios.
    for f in non_following:
        try:
            api.create_friendship(f)
            total_followed += 1
            if total_followed % 10 == 0:
                print(str(total_followed) + ' los usuarios siguieron hasta ahora.')
            print('Usuario seguido Durmiendo 10 segundos.')
            sleep(10)
        except (tweepy.RateLimitError, tweepy.TweepError) as e:
            error_handling(e)
    print(total_followed)


# Función para seguir a los seguidores de otro usuario.
def follow_all(followers, following, total_followed, whitelisted_users, blacklisted_users):
    their_name = input('Ingrese su nombre. No utilice un signo @. Por ejemplo, para @POTUS, ingrese solo POTUS: ')
    their_followers = api.followers_ids(their_name)

    # Hace una lista de seguidores no mutuos.
    their_followers_reduced = set(their_followers) - set(following) - set(blacklisted_users)
    # recorre a través de sus seguidores y seguidores y agrega relaciones no mutuas a sus seguidores reducidas

    print('Empezando a seguir a los usuarios. . .')
    # Recorre la lista y sigue a los usuarios.
    for f in their_followers_reduced:
        try:
            # Sigue al usuario.
            api.create_friendship(f)
            total_followed += 1
            if total_followed % 10 == 0:
                print(str(total_followed) + ' los usuarios siguieron hasta ahora.')
            print('Usuario seguido Durmiendo 10 segundos.')
            sleep(10)
        except (tweepy.RateLimitError, tweepy.TweepError) as e:
            error_handling(e)
    print(total_followed)


# Función para seguir a los usuarios en base a una palabra clave.
def follow_keyword(followers, following, total_followed, whitelisted_users, blacklisted_users):
    for i in config_data["keywords"]:
        # Resultado de busqueda.
        search_results = api.search(
            q=i,
            count=config_data["results_search"],
            lang=config_data["lang"])
        searched_screen_names = [tweet.author._json['screen_name'] for tweet in search_results]
        searched_screen_names = list(set(searched_screen_names) - set(blacklisted_users))

        # Seguir a 100 de cada palabra clave para evitar seguir a usuarios no relevantes.
        print('Comenzando a seguir a los usuarios que tweeted \'{}\''.format(i))
        for i in range(0, len(searched_screen_names) - 1):
            try:
                # Sigue al usuario.
                api.create_friendship(searched_screen_names[i])
                total_followed += 1
                if total_followed % 10 == 0:
                    print(str(total_followed) + ' usuarios seguidos hasta ahora.')
                print('Usuario seguido Durmiendo 10 segundos.')
                sleep(10)
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                error_handling(e)
    print(total_followed)



# Función para seguir a los usuarios que retuitearon un tweet.
def follow_rters(followers, following, total_followed, whitelisted_users, blacklisted_users):
    print("Según la API de Twitter, este método solo devuelve un máximo de 100 usuarios por tweet. \n")

    # Obtiene el ID de tweet usando expresiones regulares.
    tweet_url = input('Por favor ingrese la URL completa del tweet: ')
    try:
        tweetID = search('/status/(\d+)', tweet_url).group(1)
    except tweepy.TweepError as e:
        print(e)
        print('No se pudo obtener la ID del tweet. Inténtalo de nuevo. ')
        follow_rters()

    # Obtiene una lista de usuarios que retwitteó un tweet.
    RTUsers = api.retweeters(tweetID)
    RTUsers = set(RTUsers) - set(blacklisted_users)

    print('Empezando a seguir a los usuarios.')

    # Sigue a los ususarios.
    for f in RTUsers:
        try:
            api.create_friendship(f)
            total_followed += 1
            if total_followed % 10 == 0:
                print(str(total_followed) + ' los usuarios siguieron hasta ahora.')
            # Duerme por lo que no sigue demasiado rápido.
            print('Usuario seguido Durmiendo 10 segundos.')
            sleep(10)
        except (tweepy.RateLimitError, tweepy.TweepError) as e:
            error_handling(e)
    print(total_followed)



# Función para dejar de seguir a los usuarios que no te siguen.
def unfollow_back(followers, following, total_followed, whitelisted_users, blacklisted_users):
    print('Empezando a dejar de seguir a los usuarios....')
    # Hacer una nueva lista de usuarios que no te siguen.
    non_mutuals = set(following) - set(followers) - set(whitelisted_users)
    for f in non_mutuals:
        try:
            # Dejar de seguir.
            api.destroy_friendship(f)
            total_followed += 1
            if total_followed % 10 == 0:
                print(str(total_followed) + ' unfollowed so far.')
            print('Unfollowed user. Sleeping 15 seconds.')
            sleep(15)
        except (tweepy.RateLimitError, tweepy.TweepError) as e:
            error_handling(e)
    print(total_followed)



# Función para dejar de seguir a todos los usuarios.
def unfollow_all(followers, following, total_followed, whitelisted_users, blacklisted_users):
    # Las listas blancas de algunos usuarios.
    unfollowing_users = set(following) - set(whitelisted_users)
    print('Empezando a dejar de seguir.')
    for f in unfollowing_users:
        # Desenvuelve usuario.
        api.destroy_friendship(f)
        # Incremento total seguido de 1.
        total_followed += 1
        # Imprimir el total sin seguir cada 10.
        if total_followed % 10 == 0:
            print(str(total_followed) + ' sin seguimiento hasta ahora.')
        # Imprime sleep.
        print('Usuario no seguido. Durmiendo 8 segundos.')
        sleep(8)
    print(total_followed)


# Función para tweets favoritos basados en palabras clave
def fav_off_keyword(followers, following, total_followed, whitelisted_users, blacklisted_users):

    for i in config_data["keywords"]:
        # Obtener el resultado de busqueda.
        search_results = api.search(
            q=i,
            count=config_data["results_search"],
            lang=config_data["lang"])
        searched_tweet_ids = [tweet.id for tweet in search_results]

        # Solo sigue a 100 de cada palabra clave para evitar seguir a usuarios no relevantes.
        print('Empezando a gustar a los usuarios que tweeted \'{}\''.format(i))
        for i in range(0, len(searched_tweet_ids) - 1):
            try:
                api.create_favorite(searched_tweet_ids[i])
                total_followed += 1
                if total_followed % 10 == 0:
                    print(str(total_followed) + ' tweets me gustó hasta ahora.')
                print('Me gustó tweet. Durmiendo 12 segundos.' )
                sleep(12)
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                error_handling(e)
    print(total_followed)

# Quitar todos los favoritos.
    def unfavorite_all(followers, following, total_followed, whitelisted_users, blacklisted_users):
        total_unliked = 0
        all_favorites = api.favorites(screen_name)

    for i in all_favorites:
        try:
            api.destroy_favorite(i.id)
            total_unliked += 1
            if total_unliked % 10 == 0:
                print(str(total_unliked) + ' tweets que gustaron hasta ahora.')
            print('Tweet no le gusta. Durmiendo 8 segundos.')
            sleep(8)
        except (tweepy.RateLimitError, tweepy.TweepError) as e:
            error_handling(e)

# Envio DM a los usuarios que te siguen.
def send_dm(followers, following, total_followed, whitelisted_users, blacklisted_users):
    shuffle(followers)
    messages = config_data["messages"]
    greetings = ['Hola ',' Hola ',' Hola ', 'Hi', 'Hey', 'Hello']
    # Intenta enviar un mensaje a tus seguidores. Cambia saludo y mensaje.
    print('Empezando a enviar mensajes ... ')
    for user, message, greeting in zip(followers, cycle(messages), cycle(greetings)):
        try:
            username = api.get_user(user).screen_name
            # Envia dm.
            api.send_direct_message(user_id=user, text='{} {},\n{}'.format(greeting, username, message))
            total_followed += 1
            if total_followed % 5 == 0:
                print(str(total_followed) + ' Mensajes enviados hasta ahora.')
            print('Envió al usuario un DM. Durmiendo 45 segundos.')
            sleep(45)
        except (tweepy.RateLimitError, tweepy.TweepError) as e:
            error_handling(e)
    print(total_followed)


# Función para obtener seguidor / siguiente conteo.
def get_count(followers, following, total_followed, whitelisted_users, blacklisted_users):
    # Imprime el recuento.
    print('Sigues a {} usuarios y {} usuarios te siguen.'.format(len(following), len(followers)))
    print('Esto a veces es inexacto debido a la naturaleza de la API y las actualizaciones. Asegúrese de volver a comprobar. ')



# Funcion para manejar errores.
def error_handling(e):
    error = type(e)
    if error == tweepy.RateLimitError:
        print("Has alcanzado un límite! Dormir durante 30 minutos.")
        sleep(60 * 30)
    if error == tweepy.TweepError:
        print('UH oh. No se pudo completar la tarea. Durmiendo 10 segundos.')
        sleep(10)


# Funcion para continuar
def Continue():
    # Pregunta al usuario si desea seguir calculando, convierte a minúsculas
    keep_going = input('¿Quieres seguir? Introduzca si o no. \n'
                       '').lower()
    # Evalúa la respuesta del usuario.
    if keep_going == 'si':
        main_menu()
    elif keep_going == 'no':
        print('\n'
              'Gracias por usar el bot de Twitter!')
        quit()
    else:
        print('\n'
              'Entrada no reconocida. Inténtalo de nuevo.')


# Ejecuta la función principal, ejecuta todo lo demas.
if __name__ == "__main__":
    main_menu()

