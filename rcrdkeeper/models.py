import rethinkdb as r
from rethinkORM import RethinkModel, RethinkCollection
from werkzeug.security import generate_password_hash, check_password_hash

r.connect(db='rcrdkeeper').repl()


class Query(object):

	@classmethod
	def all(self):
		collection = RethinkCollection(self)
		return collection

	@classmethod
	def order_by(self, *field):#, direct='desc'):
		collection = RethinkCollection(self)
		collection.orderBy(field, direct=direct)
		return collection

	@classmethod
	def limit(self, value):
		collection = RethinkCollection(self)
		collection.limit(value)
		return collection

	@classmethod
	def get(self, **kwargs):
		collection = RethinkCollection(self, filter=kwargs)
		return collection.fetch()[0]

class Condition(RethinkModel, Query):
	table = "record_condition"


class Size(RethinkModel,  Query):
	table = "record_size"


class Records(RethinkModel, Query):
	table = "records"

class User(RethinkModel, Query):
	table = "users"

	@classmethod
	def auth_user(self, email, password):
		collection = RethinkCollection(self, filter={'email': email})
		get_user = collection.fetch()

		user = {}
		if not get_user:
			user['status'] = False
			user['reason'] = 'not exist'
			return user
		else:
			valid_password = check_password_hash(get_user[0]['password'],
												 password)
			if not valid_password:
				user['status'] = False
				user['reason'] = 'not password'
				return user

		user['status'] = True
		return user
