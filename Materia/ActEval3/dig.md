# Atividad Evaluada 3

1. agrimed.cl
Probamos con el resolver por defecto y no entregó ningun nombre de servido válido, fue la misma respuesta al probar con @a.nic.cl:
```
;; QUESTION SECTION:
;agrimed.cl.			IN	NS
```
La única diferencia con nic.cl es que entregaba un parámetro cookie, pero ninguna de las dos tenia answer section con la lista de serrvidores válidos

2. srcei.cl
Con el resolver por defecto: 
```
;; ANSWER SECTION:
srcei.cl.		28800	IN	NS	infoblox01.srcei.cl.
srcei.cl.		28800	IN	NS	secundario.nic.cl.
srcei.cl.		28800	IN	NS	ns.sed.srcei.cl.
srcei.cl.		28800	IN	NS	ns.srcei.cl.
```
A continuación probaremos la respuesta de cada uno de estos servidores:
- dig ns srcei.cl @infoblox01.srcei.cl
```
;; ANSWER SECTION:
srcei.cl.		28800	IN	NS	secundario.nic.cl.
srcei.cl.		28800	IN	NS	ns.srcei.cl.
srcei.cl.		28800	IN	NS	ns.sed.srcei.cl.
srcei.cl.		28800	IN	NS	infoblox01.srcei.cl.
```
- dig ns srcei.cl @secundario.nic.cl
```
;; ANSWER SECTION:
srcei.cl.		28800	IN	NS	ns.srcei.cl.
srcei.cl.		28800	IN	NS	ns.sed.srcei.cl.
srcei.cl.		28800	IN	NS	secundario.nic.cl.
srcei.cl.		28800	IN	NS	infoblox01.srcei.cl.
```
- dig ns srcei.cl @ns.srcei.cl
```
;; ANSWER SECTION:
srcei.cl.		28800	IN	NS	infoblox01.srcei.cl.
srcei.cl.		28800	IN	NS	ns.sed.srcei.cl.
srcei.cl.		28800	IN	NS	ns.srcei.cl.
srcei.cl.		28800	IN	NS	secundario.nic.cl.
```
- dig ns srcei.cl @ns.sed.srcei.cl
```
;; communications error to 119.8.144.219#53: timed out
;; communications error to 119.8.144.219#53: timed out
;; communications error to 119.8.144.219#53: timed out

; <<>> DiG 9.18.33-1~deb12u2-Debian <<>> ns srcei.cl @ns.sed.srcei.cl
;; global options: +cmd
;; no servers could be reached
```
Como el último servidor no obtuvo respuesta se puede decir que cae en una falta grave y sigue la leyenda de ~it's always dns~...

3. udi.cl
Con el resolver por default nos indica que tiene un servidor llamado ns1.maxtel.cl. Si probamos este servidor nos entregará la siguiente respuesta: 
```
;; ANSWER SECTION:
udi.cl.			3600	IN	NS	ns1.maxtel.cl.
```
Pero si probamos con el dominio padre .cl, usando el servidor de a.nic.cl obtendremos un segundo servidor válido que no estaba en la lista de ns1.maxtel.cl:
```
;; AUTHORITY SECTION:
udi.cl.			3600	IN	NS	ns1.maxtel.cl.
udi.cl.			3600	IN	NS	secundario.nic.cl.
```
El cual tiene question section más no answer section, esto indica que el servidor padre tiene una información desactualizada pero no erronea pues no se cae con timeout, lo que permite seguir consultando inmediatamente no se encuentre en éste. 