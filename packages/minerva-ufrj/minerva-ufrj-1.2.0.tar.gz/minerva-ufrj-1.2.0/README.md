# minerva
### Um renovador automático de livros da biblioteca da UFRJ

## Instalação
Requer Python3.7+, pode ser obtido via ``pip`` ou executando o script ``setup.py`` em um clone do repositório.

### Linux, OSx
```bash
$ python3 -m pip install minerva-ufrj
```
ou
```bash
$ pip3 install minerva-ufrj
```

### Windows
```shell
> pip install minerva-ufrj
```

## Uso
```
$ minerva --help
```

Para renovar os livros de uma conta use o comando:
```
minerva [user] [pswd]
```

Para guardar em cache suas credenciais:
```
minerva -c [user] [pswd]
```

Para listar as credenciais armazenadas:
```
minerva -l
```

Para renovar os livros de todas as credenciais armazenadas:
```
minerva -r
```

## Por fazer:
- Implementar configurações de renovação automática (agendada).<br>
    Algo como
    ```
    minerva --schedule
    ```
    que agende uma renovação ao conectar-se à internet.

- Implementar casos de erro ao renovar.
    Simplesmente melhores relatórios de falha.