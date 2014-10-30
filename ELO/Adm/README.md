# LETProject.ELO.Adm

## Fun��o

Pasta que cont�m o m�dulo de administra��o.
Esta parte do projeto � a respons�vel pelas p�ginas do administrador, atrav�s das quais ele poder� criar e deletar cursos, bem como matricular e desmatricular alunos ou professores e associar estes.

## Conte�do

As entradas em negrito indicam pastas, e as normais indicam arquivos isolados.

* __init__.py
* forms.py
* AdmUnit.py

## __init__.py

Arquivo requisitado pelo python para reconhecer a pasta como um reposit�rio de arquivos referenci�vel.
Em outras palavras, � um arquivo que s� � �til para a linguagem e deve ser ignorado em outras inst�ncias.

## forms.py

Arquivo que cont�m a defini��o das classes que modelam os formul�rios deste m�dulo.
Neste caso, ele � respons�vel por modelar os forms de registro de dados de um Estudante ou Professor, como dados de Nome, Matr�cula, Campus, Sexo, E-mail e Senha, e de Cursos que � requisitado um C�digo do Curso, Nome e o Professor Respons�vel. Forms de dele��o e edi��o de contas tamb�m s�o modelados neste arquivo, sendo este primeiramente coordenado com um form de procura da identidade da conta, sendo matr�cula para Estudantes e Professores e para os Cursos � requisitado o c�digo referente. E para que ocorra qualquer a��o citada acima ser� necess�rio a confirma��o de senha de administrador que tamb�m � distribu�do em um form � parte.

## AdmUnit.py

Arquivo principal do m�dulo.
Cont�m as diferentes camadas, bem como suas devidas interfaces e variadas implementa��es.
� o arquivo que � respons�vel pelo controle do sistema pelo Administrador, criando, editando e deletando contas de Estudantes e Professores, e realizando a cria��o e dele��o de Cursos. Neste arquivo � implementado m�todos que interagem com a Factory (ver MainUnit.py dentro de LETProject.ELO.ELO) para o controle geral, classes que importam os formul�rios para inser��o de dados no sistema, comunica��o com banco de dados para estas altera��es e cookies para atualiza��o das contas que foram alteradas.
Observa��o: O Administrador n�o � capaz de editar um curso, somente o Professor respons�vel poder� edit�-lo.
