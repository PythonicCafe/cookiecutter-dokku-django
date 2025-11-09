# {{ cookiecutter.project_name }}

O projeto e todos os serviços necessários (como bancos de dados) rodam completamente dentro de _containers_ Docker.
Para rodá-lo localmente, você precisará de docker, docker compose e make.

Apesar de existirem outras formas de rodar o projeto localmente (como executando o Django em um virtualenv),
recomendamos utilizar a forma descrita nesse documento, para simplificar o processo e evitar conflitos de versões.

Rodando todos os serviços:

```shell
make start logs
```

> Nota: a primeira vez que o comando acima for executado irá demorar alguns minutos, pois irá construir a imagem Docker
> que executará o Django e baixará as demais imagens/dependências. As próximas vezes serão bem mais rápidas.

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

**Atenção**: não se esqueça de executar `make restart` para que a mudança nas variáveis de ambiente faça efeito (não
adianta reiniciar apenas o container do serviço que teve variáveis alteradas, é preciso reiniciar o docker compose
completamente).

> Nota: caso você precise adicionar alguma variável de ambiente que será usada por todos da equipe obrigatoriamente,
> defina pelo menos um valor fictício no arquivo principal, para que todos consigam executar corretamente.


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
  [localhost:5000](http://localhost:5000/);
{%- if cookiecutter.enable_celery == "y" %}
- `worker`: utiliza a mesma imagem do container `web`, mas executa o worker do Celery (em vez do servidor HTTP), para
  processar as tarefas em segundo plano;
{%- endif %}
- `db`: executa o banco de dados, sem encaminhamento de porta da máquina host (você pode conectar ao shell do banco
  executando `make dbshell` ou `docker compose exec web python manage.py dbshell`);
{%- if cookiecutter.enable_mailhog == "y" %}
- `mail`: executa o Mailhog (para verificar os emails enviados), acessível em [localhost:8025](http://localhost:8025/);
{%- endif %}
{%- if cookiecutter.enable_redis == "y" %}
- `messaging`: executa o Redis (para cache e fila de tarefas), sem encaminhamento de porta da máquina host (você pode
  conectar-se a ele executando `docker compose exec messaging redis-cli`);
{%- endif %}
{%- if cookiecutter.enable_minio == "y" %}
- `storage`: executa o MinIO (equivalente ao AWS S3), acessível em [localhost:9000](http://localhost:9000/) (API) e
  [localhost:9001](http://localhost:9001/) (console).
{%- endif %}
