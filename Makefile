DATABASE_HOST?=127.0.0.1
DATABASE_PORT?=5432
DATABASE_USER?=postgres
DATABASE_NAME?=country_report


define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z0-9_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean:  ## clean working folder
	@rm -f ./~build dist

.init-db:
	psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER} -c "DROP DATABASE IF EXISTS test_${DATABASE_NAME}"
	psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER} -c "DROP DATABASE IF EXISTS ${DATABASE_NAME}"
	psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER} -c "CREATE DATABASE ${DATABASE_NAME}"

bootstrap:
	python manage.py upgrade --admin-email admin@unicef.org --admin-password 123

i18n:
	./manage.py makemessages --locale es --locale fr --locale ar --locale pt --ignore '~*'
	./manage.py compilemessages


reset-migrations: ## reset django migrations
	./manage.py check
	find src -name '0*[1,2,3,4,5,6,7,8,9,0]*' | xargs rm -f
	$(MAKE) .init-db
	./manage.py makemigrations

	gsed -i 's;operations = \[;operations = \[CITextExtension(),;' src/hope_country_report/apps/core/migrations/0001_initial.py
	gsed -i '1i from django.contrib.postgres.operations import CITextExtension' src/hope_country_report/apps/core/migrations/0001_initial.py
	isort src/hope_country_report/apps/core/migrations/0001_initial.py
	black src/hope_country_report/apps/core/migrations/0001_initial.py
	$(MAKE) bootstrap
	python manage.py demo
