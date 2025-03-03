# {{ cookiecutter.project_slug }}

Você precisará de docker, docker compose e make para executar corretamente esse projeto.

Rodando todos os serviços:

```shell
make start logs
```

Para acessar o Django, entre em [localhost:5000](http://localhost:5000). O serviço `web` do docker compose irá executar
as migrações antes de iniciar o servidor HTTP, então o sistema já estará pronto para usar (mas ainda sem dados).

Para criar um super usuário no Django (que dá acesso ao Django Admin), execute:

```shell
docker compose exec -it web python manage.py createsuperuser
# ou `make bash` e então, dentro do shell container, `python manage.py createsuperuser`
```

Para executar os testes automatizados, execute (fora do container):

```shell
make test
```

Caso queira rodar apenas algum teste específico, passe opções para o `pytest` por meio da variável `TEST_ARGS`:
```shell
TEST_ARGS="-k test_run_only_this_one" make test
```

Para forçar o guia de estilos em todo o código Python, execute (fora do container):

```shell
make lint
```

Para ver mais atalhos que ajudam no processo de desenvolvimento, execute `make help`.


## Personalizando variáveis de ambiente

Cada serviço definido no Docker compose possui um arquivo de variável de ambiente chamado `docker/env/<serviço>`. Se
você precisa trocar qualquer um dos valores padrão, crie um arquivo chamado `docker/env/<serviço>.local` e coloque-as
lá. Esse arquivo será ignorado pelo Git e o Docker compose irá carregá-lo após o primeiro, sobrescrevendo os valores.
Dessa forma, evitamos colocar credenciais e outros dados sensíveis no repositório.

> Nota: caso você precise adicionar alguma variável de ambiente que será usada por todos da equipe obrigatoriamente,
> defina pelo menos um valor fictício no arquivo principal, para que todos consigam executar corretamente.


## Serviços

Os serviços configurados no Docker compose são:



## Backup

Você pode precisar fazer backup das seguintes pastas (ou as equivalentes em produção):
- `docker/data/web` caso sua aplicação Web guarde dados em `/data`
- `docker/data/db` para o banco de dados
{%- if cookiecutter.enable_minio == "y" %}
- `docker/data/storage` para os arquivos armazenados no MinIO
{%- endif %}


## Serviços

Os serviços configurados no Docker compose são:

- `web`: container principal da aplicação Web, rodando o Django e acessível por
  [localhost:5000](http://localhost:5000/)
{%- if cookiecutter.enable_celery == "y" %}
- `worker`: utiliza a mesma imagem do container acima, mas executa o worker do Celery (em vez do servidor HTTP), para
  processar as tarefas em segundo plano
{%- endif %}
- `db`: database container, without port forwarding from the host machine (you can connect to the database shell by
  running `docker compose exec web python manage.py dbshell`)
{%- if cookiecutter.enable_mailhog == "y" %}
- `mail`: Mailhog container, acessible through [localhost:8025](http://localhost:8025)
{%- endif %}
{%- if cookiecutter.enable_redis == "y" %}
- `messaging`: redis container, without port forwarding from the host machine (you can connect to it by running
  `docker compose exec messaging redis-cli`)
{%- endif %}
{%- if cookiecutter.enable_minio == "y" %}
- `storage`: MinIO container, acessible through [localhost:9000](http://localhost:9000/) (API) and
  [localhost:9001](http://localhost:9001/) (console)
{%- endif %}
