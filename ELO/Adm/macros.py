#coding: utf-8

## @file macros.py
#
#   Arquivo contendo todas as macros utilizadas no módulo de Administração.

from django.utils.encoding import force_unicode

## Macro responsável por armazenar a URL base do template de edição de contas.
ACCOUNTS_URL = lambda x="": 'Adm/' + str(x) 

## Macro responsável por armazenar a URL do template da página incial.
HOME_URL = ACCOUNTS_URL('adm_accounts.html')

## Macro responsável por armazenar a URL do template para criação de novas
#	contas.
NEW_URL = ACCOUNTS_URL('new_acc.html')

## Macro responsável por armazenar a URL do template para edição de contas.
EDIT_URL = ACCOUNTS_URL('edit_acc.html')

## Macro responsável por armazenar a URL do template para deleção de contas.
DEL_URL = ACCOUNTS_URL('del_acc.html')






