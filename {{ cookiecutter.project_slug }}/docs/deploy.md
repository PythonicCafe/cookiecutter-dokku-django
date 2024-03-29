# Deploy do projeto

O deployment do projeto é realizado através do [Dokku](https://dokku.com/), que
facilita a gestão de containers Docker e outros serviços, como bancos de dados,
servidores de cache etc.

## Configurações iniciais do servidor

Para a segurança do servidor, é importante que você:

- Utilize apenas chaves SSH para login (copie suas chaves usando o comando
  `ssh-copy-id` ou coloque-as em `/root/.ssh/authorized_keys`)
- Remova a opção de login via SSH usando senha (altere a configuração editando
  o arquivo `/etc/ssh/ssh_config` e depois execude `service ssh restart`)
- Se possível, crie um outro usuário que possua acesso via `sudo` e desabilite
  o login do usuário root via SSH (edite o arquivo `/etc/ssh/ssh_config`)


## Instalação de pacotes básicos de sistema

```shell
apt update && apt upgrade -y && apt install -y wget
apt install -y $(wget -O - https://raw.githubusercontent.com/turicas/dotfiles/main/server-apt-packages.txt)
apt clean
```


## Instalação do Docker

Caso a versão do Debian seja mais nova que bullseye, verifique mudanças nos
comandos abaixo [na documentação do
Docker](https://docs.docker.com/engine/install/debian/).

```shell
apt remove docker docker-engine docker.io containerd runc
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Para testar:
docker run --rm hello-world
```

## Instalação e configuração do Dokku

Caso a versão do Debian seja mais nova que bullseye, verifique mudanças nos
comandos abaixo [na documentação do
Dokku](https://dokku.com/docs/getting-started/install/debian/).

```shell
wget -qO- https://packagecloud.io/dokku/dokku/gpgkey | tee /etc/apt/trusted.gpg.d/dokku.asc
OS_ID="$(lsb_release -cs 2>/dev/null || echo "bionic")"
echo "bionic focal jammy" | grep -q "$OS_ID" || OS_ID="bionic"
echo "deb https://packagecloud.io/dokku/dokku/ubuntu/ ${OS_ID} main" | tee /etc/apt/sources.list.d/dokku.list
apt update
apt install -y dokku
# Responda nas perguntas que quer habilitar vhost
apt clean
dokku plugin:install-dependencies --core

# Dokku configs
dokku config:set --global DOKKU_RM_CONTAINER=1  # don't keep `run` containers around

# Dokku plugins
dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku plugin:install https://github.com/dokku/dokku-maintenance.git
{%- if cookiecutter.database_software == "postgres" %}
dokku plugin:install https://github.com/dokku/dokku-postgres.git
{%- elif database_software == "mariadb" %}
dokku plugin:install https://github.com/dokku/dokku-mariadb.git
{%- endif %}
{% if cookiecutter.enable_celery == "y" or cookiecutter.enable_redis == "y" %}
dokku plugin:install https://github.com/dokku/dokku-redis.git
{% endif %}
dokku letsencrypt:cron-job --add
```

Caso você não tenha colocado sua chave SSH do Dokku durante a execução do
comando `apt install dokku`, você precisa adicioná-la com o seguinte comando:

```shell
dokku ssh-keys:add admin path/to/pub_key
```

> Nota: o arquivo deve ter apenas uma chave SSH (caso o arquivo fornecido na
> interface de configuração tenha mais de uma chave, a configuração precisará
> ser feita manualmente, com o comando acima).

Dessa forma, o usuário que possuir essa chave poderá fazer deployments via git
nesse servidor.

> **Importante:** após a instalação do Dokku, caso não tenha respondido às
> perguntas durante a instalação, será necessário acessar a interface Web
> temporária para finalizar configuração (entre em `http://ip-do-servidor/` em
> seu navegador).

Ao finalizar a instalação do Dokku e acessar http://ip-do-servidor/ você deverá
ver a mensagem "Welcome to nginx!".


## Instalação da aplicação

Antes de criar a aplicação no Dokku será necessário configurar algumas
variáveis no shell, para que elas sejam adicionadas às variáveis de ambiente do
app (assim, o Dokku irá sempre carregá-las toda vez que o app for iniciado e
não precisaremos armazenar senhas em arquivos no repositório).

```shell
# Provavelmente você precisará trocar apenas essas primeiras:
export APP_NAME="{{ cookiecutter.project_slug }}"
export APP_DOMAIN="myapp.example.com"  # Domínio por onde o app será acessado
export SENTRY_DSN="..."  # URL de acesso ao Sentry, para reporte de erros
export ADMINS="App Admin|admin@myapp.example.com"
export DEFAULT_FROM_EMAIL="noreply@myapp.example.com"

export LETSENCRYPT_EMAIL="$(echo $ADMINS | sed 's/^[^|]*|\([^,]*\).*$/\1/')"
export ALLOWED_HOSTS="$APP_DOMAIN"
export CSRF_TRUSTED_ORIGINS="https://${APP_DOMAIN}"
export DATA_DIR="/data"
export DEBUG="false"
export DEV_BUILD="false"
export EMAIL_BACKEND="sgbackend.SendGridBackend"
{%- if cookiecutter.database_software == "postgres" %}
export DB_NAME="pg_${APP_NAME}"
{%- elif database_software == "mariadb" %}
export DB_NAME="mdb_${APP_NAME}"
{%- endif %}
{% if cookiecutter.enable_celery == "y" or cookiecutter.enable_redis == "y" %}
export REDIS_NAME="redis_${APP_NAME}"
{% endif %}
export SECRET_KEY=$(openssl rand -base64 64 | tr -d ' \n')
export STORAGE_PATH="/var/lib/dokku/data/storage/$APP_NAME"
```

Depois que as variáveis foram definidas, podemos criar o app, os serviços de
banco de dados e fazer as configurações iniciais:

```shell
dokku apps:create $APP_NAME
dokku domains:add $APP_NAME $APP_DOMAIN
dokku nginx:set $APP_NAME client-max-body-size 50m

# Provisionando um volume (será útil para transportar dados do container para a
# máquina host, em tarefas de manutenção)
mkdir -p "$STORAGE_PATH"
chown -R 1000:1000 "$STORAGE_PATH"  # `django` user inside container have UID=GID=1000
dokku storage:mount $APP_NAME "$STORAGE_PATH:$DATA_DIR"

# Provisionando serviços de banco de dados
{%- if cookiecutter.database_software == "postgres" %}
dokku postgres:create $DB_NAME -i {{ cookiecutter.postgres_image }} -I {{ cookiecutter.postgres_version }} --shm-size {{ cookiecutter.db_shm_size }}
dokku postgres:stop $DB_NAME
# Cópia de arquivo local para o servidor remoto:
scp docker/conf/db/postgresql.prd.conf root@<servidor>:/var/lib/dokku/services/postgres/$DB_NAME/data/postgresql.conf
dokku postgres:start $DB_NAME
dokku postgres:link $DB_NAME $APP_NAME
{%- elif database_software == "mariadb" %}
dokku mariadb:create $DB_NAME -i {{ cookiecutter.mariadb_image }} -I {{ cookiecutter.mariadb_version }} --shm-size {{ cookiecutter.db_shm_size }}
dokku mariadb:link $DB_NAME $APP_NAME
{%- endif %}
{% if cookiecutter.enable_celery == "y" or cookiecutter.enable_redis == "y" %}
dokku redis:create $REDIS_NAME -i {{ cookiecutter.redis_image }} -I {{ cookiecutter.redis_version }}
dokku redis:link $REDIS_NAME $APP_NAME
{% endif %}

dokku config:set --no-restart $APP_NAME ADMINS="$ADMINS"
dokku config:set --no-restart $APP_NAME ALLOWED_HOSTS="$ALLOWED_HOSTS"
dokku config:set --no-restart $APP_NAME CSRF_TRUSTED_ORIGINS="$CSRF_TRUSTED_ORIGINS"
dokku config:set --no-restart $APP_NAME DATA_DIR="$DATA_DIR"
dokku config:set --no-restart $APP_NAME DEBUG="$DEBUG"
dokku config:set --no-restart $APP_NAME DEV_BUILD="$DEV_BUILD"
{%- if cookiecutter.enable_mailhog == "y" %}
dokku config:set --no-restart $APP_NAME DEFAULT_FROM_EMAIL="..."
dokku config:set --no-restart $APP_NAME EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
dokku config:set --no-restart $APP_NAME EMAIL_HOST="..."
dokku config:set --no-restart $APP_NAME EMAIL_HOST_PASSWORD="..."
dokku config:set --no-restart $APP_NAME EMAIL_HOST_USER="..."
dokku config:set --no-restart $APP_NAME EMAIL_PORT="..."
dokku config:set --no-restart $APP_NAME EMAIL_USE_SSL="..."
dokku config:set --no-restart $APP_NAME EMAIL_USE_TLS="..."
{%- endif %}
dokku config:set --no-restart $APP_NAME SECRET_KEY="$SECRET_KEY"
{%- if cookiecutter.enable_sentry == "y" %}
dokku config:set --no-restart $APP_NAME SENTRY_DSN="$SENTRY_DSN"
{%- endif %}
```

Com o app criado e configurado, agora precisamos fazer o primeiro deployment,
para então finalizar a configuração com a criação do certificado SSL via Let's
Encrypt (precisa ser feito nessa ordem).

Em sua **máquina local**, vá até a pasta do repositório e execute:

```shell
# Troque <server-ip> pelo IP do servidor e <app-name> pelo valor colocado na
# variável $APP_NAME definida no servidor
# ATENÇÃO: execute esses comandos fora do servidor (em sua máquina local)
git remote add dokku dokku@<server-ip>:<app-name>
git checkout main
git push dokku main
```

Para finalizar as configurações iniciais, conecte novamente no servidor e
execute:

```shell
dokku letsencrypt:set $APP_NAME email "$LETSENCRYPT_EMAIL"
dokku letsencrypt:enable $APP_NAME
dokku checks:disable $APP_NAME
dokku ps:scale $APP_NAME web={{ cookiecutter.dokku_web_workers }}
{% if cookiecutter.enable_celery == "y" %}
dokku ps:scale $APP_NAME worker={{ cookiecutter.celery_workers }}
{% endif %}
```

Aplicação instalada e rodando! Para criar um superusuário no Django:

```shell
dokku run $APP_NAME python manage.py createsuperuser
```

{% if cookiecutter.enable_minio == "y" %}
## MinIO

O sistema necessita de uma instância do MinIO rodando. Para fazer o _deployment_ do MinIO em um servidor Dokku, siga as
instruções do repositório [PythonicCafe/dokku-minio](https://github.com/PythonicCafe/dokku-minio/).
{% endif %}
