[:uk: English](/) | :brazil: **Português**

# FrostSense

Solução IoT de monitoramento em tempo real da temperatura de frigoríficos.

![Print do FrostSense, página Readings](screenshots/readings.png)
![Print do FrostSense, página History](screenshots/history.png)
![Print do FrostSense, página Reports](screenshots/reports.png)

- Leituras de temperatura multi-sensor em tempo real
- Relatórios customizáveis (sensor, formato de dados, período, observações)
- Verificação de relatórios por código único
- Suporte a Celsius e Fahrenheit
- Gerenciamento de usuários com sistema de permissões
- Preferências de usuário
- Configurações do sistema
- API com autenticação por chave de sensor
- Interface totalmente responsiva
- CLI para tarefas técnicas


## Instalação

Primeiramente, certifique-se de que o MariaDB está instalado e rodando.
[Veja o guia de instalação (inglês)](https://mariadb.com/get-started-with-mariadb/).

1. Clone o repositório:
    ```sh
    git clone https://github.com/purewave0/FrostSense.git
    cd FrostSense
    ```

2. Instale as dependências:
    ```sh
    pip install -r requirements.txt
    ```

3. Crie um arquivo `.env` na raiz do projeto com a seguinte configuração de
exemplo:
    ```properties
    DATABASE_URL=mariadb://USUARIO:SENHA@localhost:3306/NOME_DO_BANCO_DE_DADOS
    SECRET_KEY=SUA_CHAVE_SECRETA
    DEBUG=False
    ```

    Altere valores conforme necessário.


## Utilização

Para rodar o FrostSense, execute:
```sh
flask run
```

Uma conta admin será automaticamente criada; credenciais temporárias serão exibidas
no terminal e salvas em `ADMIN-ACCOUNT.txt` na raiz do projeto.

Acesse a interface web em `http://localhost:5000` e logue na conta admin.
Você será solicitado a criar uma nova senha.

### Sensores e leituras

Após logar, vá para a página **Sensors**; você verá que está vazia. Vamos criar alguns
sensores:
```sh
flask seed sensors  # opcional: --count=N para criar N sensores (padrão: 4)
```

Você (e qualquer usuário com permissão de edição) pode renomear um sensor passando
o mouse sobre ele e clicando no ícone de Editar.

Agora, vá ou para **Readings** (dados mais recentes) ou **History** (dados por dia).
Os sensores estão vazios, então vamos inserir algumas leituras de exemplo.
```sh
flask seed readings --continuous
```

Isso enviará leituras a cada 2 segundos (customize com `--interval=N`). Se você preferir
enviar várias leituras duma vez, execute:
```sh
flask seed readings
```

Você verá imediatamente os dados novos chegando.

### Gerenciamento de Usuários

O gerenciamento de usuários é destinado ao admin, sendo feito na página **Users**.

Inicialmente, a tabela estará vazia; vamos adicionar alguns usuários.

Embora seja possível fazer isso pelo botão **Create**, tente inserí-los pelo CLI:
```sh
flask seed users  # opcional: --count=N (padrão: 4)
```

Passe o mouse sobre alguma linha de usuário para ver as ações (editar, resetar senha,
deletar).

Passe o mouse sobre a célula de Permissões em alguma linha de usuário para ver as
permissões do mesmo.

#### Recuperação

Se a senha do admin for perdida ou vazada, resete-a com:
```sh
flask admin reset-password
# > ...
# > new temporary password (nova senha temporária): xxxxxxxxxxxx
```

Ao logar, você será solicitado a criar uma nova senha.

### Preparando dispositivos sensores

O gerenciamento de sensores é destinado aos técnicos e limitado ao CLI.

Cada sensor possui uma chave única usada pela API para autenticar as leituras
recebidas. Isso evita leituras falsas de dispositivos desconhecidos.

Um **dispositivo** pode ser qualquer coisa que possa se conectar a um sensor de
temperatura e enviar requisições HTTP: placas ESP32, Raspberry Pis, etc.

Ao preparar um novo dispositivo, primeiro crie um novo sensor:
```sh
flask sensors create SENSOR_NAME
# > created sensor with id=SENSOR_ID (criado sensor de id=...ID_DO_SENSOR)
```

Use o ID exibido pelo comando (ou procure-o usando `flask sensors list`) para obter
a chave do sensor recém-criado:
```sh
flask sensors show ID_DO_SENSOR
# > ...
# > key (chave): xxxxxxxxxxxxxxxxxxxxxxxx
```

Armazene a chave na placa/dispositivo para incluí-la com todas requisições (veja a
próxima seção).

Se uma chave de sensor for vazada, resete-a com:
```sh
flask sensors reset-key ID_DO_SENSOR
# > ...
# > new key (nova chave): xxxxxxxxxxxxxxxxxxxxxxxx
```

O dispositivo com a chave antiga não poderá mais enviar leituras.

Para deletar um sensor, obtenha o ID dele com `flask sensors list` e execute:
```sh
flask sensors delete ID_DO_SENSOR
```

### Enviando leituras

Para enviar uma leitura, o dispositivo deve enviar uma requisição POST para
`/api/sensors/<ID_DO_SENSOR>` com o valor do cabeçalho `Authorization` igual à chave
do sensor, e com o seguinte corpo JSON:
```js
{
    "temperature": TEMPERATURA,  // em Celsius
}
```

Temperaturas devem ser enviadas em Celsius.

HTTP 204 indica sucesso.


## Testes

Primeiro, instale as dependências:
```sh
pip3 install -r requirements-dev.txt
```

Execute todos os testes com:
```sh
python3 -m pytest
```

## TODO

- Documentação da API com Swagger
- Internacionalização do frontend

## Créditos

- [Google's Material Symbols](https://fonts.google.com/icons) pelos ícones SVG
- [Google Fonts](https://fonts.google.com/) pela fonte Roboto
