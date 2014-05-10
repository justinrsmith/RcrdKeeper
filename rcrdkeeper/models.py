import rethinkdb as r
from rethinkORM import RethinkModel, RethinkCollection
from werkzeug.security import generate_password_hash, check_password_hash

r.connect(db='rcrdkeeper').repl()


class Query(object):

	@classmethod
	def order_by(self, key1, *args):
		collection = RethinkCollection(self)
		collection.order_by(key1, *args)
		return collection

	@classmethod
	def get(self, **kwargs):
		collection = RethinkCollection(self, filter=kwargs)
		results = collection.fetch()

		if results:
			return results[0]
		else:
			return None

	@classmethod
	def filter(self, **kwargs):
		collection = RethinkCollection(self, filter=kwargs)
		return collection 


class Wish_List(RethinkModel, Query):
	table = 'wish_list'


class Condition(RethinkModel, Query):
	table = 'record_condition'


class Size(RethinkModel,  Query):
	table = 'record_size'


class Records(RethinkModel, Query):
	table = 'records'


class Contact(RethinkModel):
	table = 'contact'


class User(RethinkModel, Query):
	table = 'users'

	@classmethod
	def auth_user(self, email, password):
		collection = RethinkCollection(self, filter={'email': email})
		get_user = collection.fetch()

		user = {}
		if not get_user:
			user['status'] = False
			user['is_user'] = False
			return user
		else:
			valid_password = check_password_hash(get_user[0]['password'],
												 password)
			if not valid_password:
				user['status'] = False
				user['valid_password'] = False
				user['is_user'] = True
				return user

		user['status'] = True
		return user
