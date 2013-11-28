from rdio import Rdio
rdio = Rdio(('zq33ap8e526smhskzx7xkghf', 'rudg3ASW2T'))
reflektor = rdio.call('search', {'query': 'settle', 'types': 'album'})

if (reflektor['status'] == 'ok'):
    print reflektor['result']['results'][0]['artist']#['results'][0]['icon']
else:
    print reflektor['message']
#print reflektor['status']
#print reflektor['message']