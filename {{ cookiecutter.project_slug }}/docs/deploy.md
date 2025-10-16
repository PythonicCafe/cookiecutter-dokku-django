# Deploy do projeto

O deployment do projeto é realizado utilizando o [Dokku](https://dokku.com/), que facilita a gestão de containers
Docker e outros serviços, como bancos de dados, servidores de cache etc. (é um *platform-as-a-service* software livre).


## Configurações iniciais do servidor

Para a segurança do servidor, é importante que você:

- Utilize apenas chaves SSH para login (copie suas chaves usando o comando `ssh-copy-id` ou coloque-as em
  `/root/.ssh/authorized_keys`)
- Remova a opção de login via SSH usando senha (altere a configuração editando o arquivo `/etc/ssh/ssh_config` e depois
  execude `service ssh restart`)
- Se possível, crie um outro usuário que possua acesso via `sudo` e desabilite o login do usuário root via SSH (edite o
  arquivo `/etc/ssh/ssh_config`)


## Instalação de pacotes básicos de sistema

```shell
apt update && apt upgrade -y && apt install -y wget
apt install -y $(wget -O - https://raw.githubusercontent.com/turicas/dotfiles/main/server-apt-packages.txt)
apt clean
```


## Instalação do Docker

Caso a versão do Debian seja mais nova que bookworm, verifique mudanças nos comandos abaixo [na documentação do
Docker](https://docs.docker.com/engine/install/debian/).

```shell
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do apt remove $pkg; done
apt update
apt install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Para testar:
docker run --rm hello-world
```

## Instalação e configuração do Dokku

Caso a versão do Debian seja mais nova que bookworm, verifique mudanças nos comandos abaixo [na documentação do
Dokku](https://dokku.com/docs/getting-started/install/debian/).

```shell
wget -qO- https://packagecloud.io/dokku/dokku/gpgkey | tee /etc/apt/trusted.gpg.d/dokku.asc
# programmatically determine distro and codename
DISTRO="$(awk -F= '$1=="ID" { print tolower($2) ;}' /etc/os-release)"
OS_ID="$(awk -F= '$1=="VERSION_CODENAME" { print tolower($2) ;}' /etc/os-release)"
echo "deb https://packagecloud.io/dokku/dokku/${DISTRO}/ ${OS_ID} main" | tee /etc/apt/sources.list.d/dokku.list
apt update
apt install -y dokku
# Responda nas perguntas que quer habilitar vhost
apt clean
dokku plugin:install-dependencies --core

# Dokku plugins
dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku plugin:install https://github.com/dokku/dokku-maintenance.git
{%- if cookiecutter.database_software == "postgres" %}
dokku plugin:install https://github.com/dokku/dokku-postgres.git
{%- elif cookiecutter.database_software == "mariadb" %}
dokku plugin:install https://github.com/dokku/dokku-mariadb.git
{%- endif %}
{% if cookiecutter.enable_celery == "y" or cookiecutter.enable_redis == "y" %}
dokku plugin:install https://github.com/dokku/dokku-redis.git
{%- endif %}

# Dokku configs
dokku config:set --global DOKKU_RM_CONTAINER=1  # don't keep `run` containers around
dokku letsencrypt:cron-job --add
```

Caso você não tenha colocado sua chave SSH do Dokku durante a execução do comando `apt install dokku`, você precisa
adicioná-la com o seguinte comando:

```shell
dokku ssh-keys:add admin path/to/pub_key
```

> Nota: o arquivo deve ter apenas uma chave SSH (caso o arquivo fornecido na interface de configuração tenha mais de
> uma chave, a configuração precisará ser feita manualmente, com o comando acima).

Dessa forma, o usuário que possuir essa chave poderá fazer deployments via git nesse servidor.

> **Importante:** após a instalação do Dokku, caso não tenha respondido às perguntas durante a instalação, será
> necessário acessar a interface Web temporária para finalizar configuração (entre em `http://ip-do-servidor/` em seu
> navegador).

Ao finalizar a instalação do Dokku e acessar `http://ip-do-servidor/` você deverá ver a mensagem "Welcome to nginx!".


## Instalação da aplicação

Antes de criar a aplicação no Dokku será necessário configurar algumas variáveis no shell, para que elas sejam
adicionadas às variáveis de ambiente do app (assim, o Dokku irá sempre carregá-las toda vez que o app for iniciado e
não precisaremos armazenar senhas em arquivos no repositório).

> Nota: recomenda-se o uso do `byobu`, que permite abrir vários terminais dentro do servidor e persiste os shells
> abertos mesmo que sua conexão SSH com o servidor caia.


```shell
# Provavelmente você precisará trocar apenas essas primeiras:
export APP_NAME="{{ cookiecutter.project_slug }}"
export APP_DOMAINS="myapp.example.com,another.example.com"  # Domínio por onde o app será acessado
{%- if cookiecutter.enable_sentry == "y" %}
export SENTRY_DSN="..."  # URL de acesso ao Sentry, para reporte de erros
{%- endif %}
export ADMINS="App Admin|admin@myapp.example.com"
export DEFAULT_FROM_EMAIL="noreply@myapp.example.com"
{%- if cookiecutter.enable_mailhog == "y" %}
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
export DEFAULT_FROM_EMAIL="noreply@myapp.example.com"
export EMAIL_HOST="..."
export EMAIL_HOST_PASSWORD="..."
export EMAIL_HOST_USER="..."
export EMAIL_PORT="..."
export EMAIL_USE_SSL="..."
export EMAIL_USE_TLS="..."
export EMAIL_TIMEOUT="15"
{% endif %}
export ENV_TYPE="production" # Or 'staging'
{%- if cookiecutter.use_hugging_face == "y" %}
export HF_HUB_CACHE="/data/cache/hf-models/"
{%- endif %}
{%- if cookiecutter.use_openai_client == "y" %}
export TIKTOKEN_CACHE_DIR="/data/cache/tiktoken"
{%- endif %}

export LETSENCRYPT_EMAIL="$(echo $ADMINS | sed 's/^[^|]*|\([^,]*\).*$/\1/')"
export ALLOWED_HOSTS="$APP_DOMAINS"
export CSRF_TRUSTED_ORIGINS="$(echo https://$APP_DOMAINS | sed 's/,/,https:\/\//g')"
export DATA_DIR="/data"
export DEBUG="false"
{%- if cookiecutter.database_software == "postgres" %}
export DB_NAME="pg_${APP_NAME}"
{%- elif cookiecutter.database_software == "mariadb" %}
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
dokku domains:set $APP_NAME $(echo $APP_DOMAINS | tr ',' ' ')
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
{%- elif cookiecutter.database_software == "mariadb" %}
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
{%- if cookiecutter.enable_mailhog == "y" %}
dokku config:set --no-restart $APP_NAME DEFAULT_FROM_EMAIL="$DEFAULT_FROM_EMAIL"
dokku config:set --no-restart $APP_NAME EMAIL_BACKEND="$EMAIL_BACKEND"
dokku config:set --no-restart $APP_NAME EMAIL_HOST="$EMAIL_HOST"
dokku config:set --no-restart $APP_NAME EMAIL_HOST_PASSWORD="$EMAIL_HOST_PASSWORD"
dokku config:set --no-restart $APP_NAME EMAIL_HOST_USER="$EMAIL_HOST_USER"
dokku config:set --no-restart $APP_NAME EMAIL_PORT="$EMAIL_PORT"
dokku config:set --no-restart $APP_NAME EMAIL_USE_SSL="$EMAIL_USE_SSL"
dokku config:set --no-restart $APP_NAME EMAIL_USE_TLS="$EMAIL_USE_TLS"
dokku config:set --no-restart $APP_NAME EMAIL_TIMEOUT="$EMAIL_TIMEOUT"
{%- endif %}
dokku config:set --no-restart $APP_NAME ENV_TYPE="$ENV_TYPE"
dokku config:set --no-restart $APP_NAME SECRET_KEY="$SECRET_KEY"
{%- if cookiecutter.enable_sentry == "y" %}
dokku config:set --no-restart $APP_NAME SENTRY_DSN="$SENTRY_DSN"
{%- endif %}
{%- if cookiecutter.use_hugging_face == "y" %}
dokku config:set --no-restart $APP_NAME HF_HUB_CACHE="$HF_HUB_CACHE"
{%- endif %}
{%- if cookiecutter.use_openai_client == "y" %}
dokku config:set --no-restart $APP_NAME TIKTOKEN_CACHE_DIR="$TIKTOKEN_CACHE_DIR"
{%- endif %}
dokku checks:disable $APP_NAME
```
{%- if cookiecutter.database_software == "postgres" %}
Caso queira alterar a versão do postgres, atualize o arquivo de configuração da versão correspondente executando:
```shell
docker run --rm -v "$(pwd)/docker/conf/db/:/data" postgres:17.4-bookworm cp ./usr/share/postgresql/postgresql.conf.sample /data/postgresql.prd.conf
```
{%- endif %}

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
dokku ps:scale $APP_NAME web={{ cookiecutter.dokku_web_workers }}
{% if cookiecutter.enable_celery == "y" %}
dokku ps:scale $APP_NAME worker={{ cookiecutter.celery_workers_production }}
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
{%- endif -%}
