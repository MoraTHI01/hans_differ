# Setup Matomo

The backend including matomo containers should be already running.
In order to run and config matomo you need installed ssl certificates, e.g. on a nginx reverse proxy container.
The following setup assumes the backend and frontend is hosted behind an own nginx reverse proxy container.
For local development it is currently not necessary to adapt the configuration.

## Configuration

Edit `data/matomo/config/config.ini.php` to
[configure Matomo behind nginx reverse proxy](https://matomo.org/faq/how-to-install/faq_98).

- Default:

```bash
salt = "0815"
trusted_hosts[] = "matomo-webserver"
trusted_hosts[] = "localhost"
login_allow_logme = 1
```

- Edited:

```bash
salt = "0815"
trusted_hosts[] = "hans-backend-webserver:8089"
login_allow_logme = 1
assume_secure_protocol = 1
force_ssl = 1
proxy_client_headers[] = HTTP_X_FORWARDED_FOR
proxy_client_headers[] = HTTP_X_REAL_IP
proxy_client_headers[] = HTTP_X_FORWARDED_PROTO
proxy_host_headers[] = HTTP_X_FORWARDED_HOST
visitor_log_maximum_actions_per_visit = 2000
```

See [visitor log maximum actions](https://matomo.org/faq/how-to/how-do-i-see-all-user-interactions-in-visitor-profiles-to-go-beyond-the-limit-more-pages-by-this-visitor-are-not-displayed/)

## Login

Use e.g. [http://localhost:8089/matomo-analytics](http://localhost:8089/matomo-analytics) to login into Matomo using
the credentials specified in `.env.config` in your root directory.
Check `HANS_BACKEND_MATOMO_USER` and `HANS_BACKEND_MATOMO_PASSWORD` accordingly.

## Database Setup

```bash
Database Server: matomo-db
Login: root
Password:
Database Name: matomo
```

```bash
Superuser:
Superuser login: choose
Password: choose
Email: choose
```

## Setup HAnS Website Tracking

- Website name: `HAnS`
- Website URL: (local: <https://localhost>)
- Website timezone: `Germany - Berlin`
- E-commerce: `Not an Ecommerce site`

## Setup Custom Variables

- Install [Custom Variables Plugin](https://github.com/matomo-org/plugin-CustomVariables/wiki) via Marketplace on your
  matomo instance to receive evaluation id's of an evaluation session
