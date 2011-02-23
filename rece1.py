#!/usr/bin/python
# -*- coding: latin-1 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

"M�dulo de Intefase para archivos de texto (mercado interno versi�n 1)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2010 Mariano Reingart"
__license__ = "GPL 3.0"
__version__ = "1.26a"

import datetime
import os
import sys
import time
import traceback
from ConfigParser import SafeConfigParser

# revisar la instalaci�n de pyafip.ws:
import wsaa, wsfev1
from php import SimpleXMLElement, SoapClient, SoapFault, date


HOMO = True
DEBUG = False
XML = False
CONFIG_FILE = "rece.ini"

LICENCIA = """
rece1.py: Interfaz de texto para generar Facturas Electr�nica Mercado Interno V1
Copyright (C) 2010 Mariano Reingart reingart@gmail.com

Este progarma es software libre, se entrega ABSOLUTAMENTE SIN GARANTIA
y es bienvenido a redistribuirlo bajo la licencia GPLv3.

Para informaci�n adicional sobre garant�a, soporte t�cnico comercial
e incorporaci�n/distribuci�n en programas propietarios ver PyAfipWs:
http://www.sistemasagiles.com.ar/trac/wiki/PyAfipWs
"""

# definici�n del formato del archivo de intercambio:
N = 'Numerico'
A = 'Alfanumerico'
I = 'Importe'
ENCABEZADO = [
    ('tipo_reg', 1, N), # 0: encabezado
    ('fecha_cbte', 8, A),
    ('tipo_cbte', 2, N), ('punto_vta', 4, N),
    ('cbt_desde', 8, N), 
    ('cbt_hasta', 8, N), 
    ('concepto', 1, N), # 1:bienes, 2:servicios,... 
    ('tipo_doc', 2, N), # 80
    ('nro_doc', 11, N), # 50000000016    
    ('imp_total', 15, I, 3), 
    ('imp_tot_conc', 15, I, 3), 
    ('imp_tot_conc', 15, I, 3), 
    ('imp_neto', 15, I, 3), 
    ('imp_iva', 15, I, 3), 
    ('imp_trib', 15, I, 3), 
    ('imp_op_ex', 15, I, 3), 
    ('moneda_id', 3, A),
    ('moneda_ctz', 10, I, 6), #10,6
    ('fecha_venc_pago', 8, A),   # opcional solo conceptos 2 y 3
    ('cae', 14, N), ('fch_venc_cae', 8, A),
    ('resultado', 1, A), 
    ('motivos_obs', 1000, A),
    ('err_code', 6, A),
    ('err_msg', 1000, A),
    ('reproceso', 1, A),
    ('emision_tipo', 4, A),
    ]
                   
#DETALLE = [
#    ('tipo_reg', 1, N), # 1: detalle item
#    ('codigo', 30, A),
#    ('qty', 12, I),
#    ('umed', 2, N),
#    ('precio', 12, I, 3),
#    ('imp_total', 14, I, 3),
#    ('ds', 4000, A),
#    ]

TRIBUTO = [
    ('tipo_reg', 1, N), # 1: tributo
    ('id', 16, A),
    ('desc', 100, A),
    ('base_imp', 15, I, 3), 
    ('alic', 15, I, 3), 
    ('importe', 15, I, 3), 
    ]

IVA = [
    ('tipo_reg', 1, N), # 2: tributo
    ('id', 16, A),
    ('base_imp', 15, I, 3), 
    ('importe', 15, I, 3), 
    ]


                    
CMP_ASOC = [
    ('tipo_reg', 1, N), # 3: comprobante asociado
    ('tipo', 3, N), ('pto_vta', 4, N),
    ('nro', 8, N), 
    ]


def leer(linea, formato):
    dic = {}
    comienzo = 1
    for fmt in formato:    
        clave, longitud, tipo = fmt[0:3]
        dec = len(fmt)>3 and fmt[3] or 2
        valor = linea[comienzo-1:comienzo-1+longitud].strip()
        try:
            if tipo == N:
                if valor:
                    valor = str(int(valor))
                else:
                    valor = '0'
            elif tipo == I:
                if valor:
                    try:
                        valor = valor.strip(" ")
                        valor = float(("%%s.%%0%sd" % dec) % (int(valor[:-dec] or '0'), int(valor[-dec:] or '0')))
                    except ValueError:
                        raise ValueError("Campo invalido: %s = '%s'" % (clave, valor))
                else:
                    valor = 0.00
            else:
                valor = valor.decode("ascii","ignore")
            dic[clave] = valor

            comienzo += longitud
        except Exception, e:
            raise ValueError("Error al leer campo %s pos %s val '%s': %s" % (
                clave, comienzo, valor, str(e)))
    return dic

def escribir(dic, formato):
    linea = " " * 335
    comienzo = 1
    for fmt in formato:
        clave, longitud, tipo = fmt[0:3]
        dec = len(fmt)>3 and fmt[3] or 2
        if clave.capitalize() in dic:
            clave = clave.capitalize()
        s = dic.get(clave,"")
        if isinstance(s, unicode):
            s = s.encode("latin1")
        valor = str(s)
        if tipo == N and valor and valor!="NULL":
            valor = ("%%0%dd" % longitud) % int(valor)
        elif tipo == I and valor:
            valor = ("%%0%dd" % longitud) % (float(valor)*(10**dec))
        else:
            valor = ("%%0%ds" % longitud) % valor
        linea = linea[:comienzo-1] + valor + linea[comienzo-1+longitud:]
        comienzo += longitud
    return linea + "\n"

def autenticar(cert, privatekey, url):
    "Obtener el TA"
    TA = "TA.xml"
    ttl = 60*60*5
    if not os.path.exists(TA) or os.path.getmtime(TA)+(ttl)<time.time():
        import wsaa
        tra = wsaa.create_tra(service="wsfe",ttl=ttl)
        cms = wsaa.sign_tra(str(tra),str(cert),str(privatekey))
        ta_string = wsaa.call_wsaa(cms,wsaa_url,trace=DEBUG)
        open(TA,"w").write(ta_string)
    ta_string=open(TA).read()
    ta = SimpleXMLElement(ta_string)
    token = str(ta.credentials.token)
    sign = str(ta.credentials.sign)
    return token, sign

def autorizar(ws, entrada, salida, informar_caea=False):
    tributos = []
    ivas = []
    cbtasocs = []
    encabezado = {}
    for linea in entrada:
        if str(linea[0])=='0':
            encabezado = leer(linea, ENCABEZADO)
        elif str(linea[0])=='1':
            tributo = leer(linea, TRIBUTO)
            tributos.append(tributo)
        elif str(linea[0])=='2':
            iva = leer(linea, IVA)
            ivas.append(iva)
        elif str(linea[0])=='3':
            cbtasoc = leer(linea, CMP_ASOC)
            cbtasocs.append(cbtasoc)
        else:
            print "Tipo de registro incorrecto:", linea[0]

    if informar_caea:
        if '/testing' in sys.argv:
            encabezado['cae'] = '21073372218437'
        encabezado['caea'] = encabezado['cae']

    ws.CrearFactura(**encabezado)
    for tributo in tributos:
        ws.AgregarTributo(**tributo)
    for iva in ivas:
        ws.AgregarIva(**iva)
    for cbtasoc in cbtasocs:
        ws.AgregarCmpAsoc(**cbtasoc)

    if DEBUG:
        print '\n'.join(["%s='%s'" % (k,str(v)) for k,v in ws.factura.items()])
    if not DEBUG or raw_input("Facturar?")=="S":
        if not informar_caea:
            cae = ws.CAESolicitar()
            dic = ws.factura
        else:
            cae = ws.CAEARegInformativo()
            dic = ws.factura
        dic.update({
            'cae':cae,
            'fch_venc_cae': ws.Vencimiento,
            'resultado': ws.Resultado,
            'motivos_obs': ws.Obs,
            'err_code': ws.ErrCode,
            'err_msg': ws.ErrMsg,
            'reproceso': ws.Reproceso,
            'emision_tipo': ws.EmisionTipo,
            })
        escribir_factura(dic, salida)
        print "NRO:", dic['cbt_desde'], "Resultado:", dic['resultado'], "%s:" % ws.EmisionTipo,dic['cae'],"Obs:",dic['motivos_obs'], "Err:", dic['err_msg'], "Reproceso:", dic['reproceso']

def escribir_factura(dic, archivo):
    dic['tipo_reg'] = 0
    archivo.write(escribir(dic, ENCABEZADO))
    for it in dic['tributos']:
        it['tipo_reg'] = 1
        archivo.write(escribir(it, TRIBUTO))
    for it in dic['iva']:
        it['tipo_reg'] = 2
        archivo.write(escribir(it, IVA))
    for it in dic['cbtes_asoc']:
        it['tipo_reg'] = 3
        archivo.write(escribir(it, CMP_ASOC))
            
def depurar_xml(client):
    fecha = time.strftime("%Y%m%d%H%M%S")
    f=open("request-%s.xml" % fecha,"w")
    f.write(client.xml_request)
    f.close()
    f=open("response-%s.xml" % fecha,"w")
    f.write(client.xml_response)
    f.close()

if __name__ == "__main__":
    if '/ayuda' in sys.argv:
        print LICENCIA
        print
        print "Opciones: "
        print " /ayuda: este mensaje"
        print " /dummy: consulta estado de servidores"
        print " /prueba: genera y autoriza una factura de prueba (no usar en producci�n!)"
        print " /ult: consulta �ltimo n�mero de comprobante"
        print " /debug: modo depuraci�n (detalla y confirma las operaciones)"
        print " /formato: muestra el formato de los archivos de entrada/salida"
        print " /get: recupera datos de un comprobante autorizado previamente (verificaci�n)"
        print " /xml: almacena los requerimientos y respuestas XML (depuraci�n)"
        print
        print "Ver rece.ini para par�metros de configuraci�n (URL, certificados, etc.)"
        sys.exit(0)

    config = SafeConfigParser()
    config.read(CONFIG_FILE)
    cert = config.get('WSAA','CERT')
    privatekey = config.get('WSAA','PRIVATEKEY')
    cuit = config.get('WSFEv1','CUIT')
    if '/entrada' in sys.argv:
        entrada = sys.argv[sys.argv.index("/entrada")+1]
    else:
        entrada = config.get('WSFEv1','ENTRADA')
    salida = config.get('WSFEv1','SALIDA')
    
    if config.has_option('WSAA','URL') and not HOMO:
        wsaa_url = config.get('WSAA','URL')
    else:
        wsaa_url = wsaa.WSAAURL
    if config.has_option('WSFEv1','URL') and not HOMO:
        wsfev1_url = config.get('WSFEv1','URL')
    else:
        wsfev1_url = None

    if config.has_option('WSFEv1','REPROCESAR'):
        wsfev1_reprocesar = config.get('WSFEv1','REPROCESAR') == 'S'
    else:
        wsfev1_reprocesar = None

    if '/debug'in sys.argv:
        DEBUG = True

    if '/xml'in sys.argv:
        XML = True

    if DEBUG:
        print "wsaa_url %s\nwsfev1_url %s\ncuit %s" % (wsaa_url, "", cuit)
    
    try:
        ws = wsfev1.WSFEv1()
        ws.Conectar(".", wsfev1_url)
        ws.Cuit = cuit
        if wsfev1_reprocesar is not None:
            ws.Reprocesar = wsfev1_reprocesar

        if '/dummy' in sys.argv:
            print "Consultando estado de servidores..."
            ws.Dummy()
            print "AppServerStatus", ws.AppServerStatus
            print "DbServerStatus", ws.DbServerStatus
            print "AuthServerStatus", ws.AuthServerStatus
            sys.exit(0)

        if '/formato' in sys.argv:
            print "Formato:"
            for msg, formato in [('Encabezado', ENCABEZADO), ('Tributo', TRIBUTO), ('Iva', IVA), ('Comprobante Asociado', CMP_ASOC)]:
                comienzo = 1
                print "== %s ==" % msg
                for fmt in formato:
                    clave, longitud, tipo = fmt[0:3]
                    dec = len(fmt)>3 and fmt[3] or (tipo=='I' and '2' or '')
                    print " * Campo: %-20s Posici�n: %3d Longitud: %4d Tipo: %s Decimales: %s" % (
                        clave, comienzo, longitud, tipo, dec)
                    comienzo += longitud
            sys.exit(0)

        # TODO: esto habr�a que guardarlo en un archivo y no tener que autenticar cada vez
        token, sign = autenticar(cert, privatekey, wsaa_url)
        ws.Token = token
        ws.Sign = sign
        
        if '/prueba' in sys.argv:
            # generar el archivo de prueba para la pr�xima factura
            tipo_cbte = 1
            punto_vta = 4002
            cbte_nro = int(ws.CompUltimoAutorizado(tipo_cbte, punto_vta))
            fecha = datetime.datetime.now().strftime("%Y%m%d")
            concepto = 1
            tipo_doc = 80; nro_doc = "33693450239"
            cbt_desde = cbte_nro + 1; cbt_hasta = cbte_nro + 1
            imp_total = "122.00"; imp_tot_conc = "0.00"; imp_neto = "100.00"
            imp_iva = "21.00"; imp_trib = "1.00"; imp_op_ex = "0.00"
            fecha_cbte = fecha; fecha_venc_pago = None # fecha
            # Fechas del per�odo del servicio facturado (solo si concepto = 1?)
            fecha_serv_desde = fecha; fecha_serv_hasta = fecha
            moneda_id = 'PES'; moneda_ctz = '1.000'

            ws.CrearFactura(concepto, tipo_doc, nro_doc, tipo_cbte, punto_vta,
                cbt_desde, cbt_hasta, imp_total, imp_tot_conc, imp_neto,
                imp_iva, imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago, 
                fecha_serv_desde, fecha_serv_hasta, #--
                moneda_id, moneda_ctz)
            
            if tipo_cbte not in (1, 2, 6, 7):
                tipo = 1
                pto_vta = 2
                nro = 1234
                ws.AgregarCmpAsoc(tipo, pto_vta, nro)
            
            id = 99
            desc = 'Impuesto Municipal Matanza'
            base_imp = 100
            alic = 1
            importe = 1
            ws.AgregarTributo(id, desc, base_imp, alic, importe)

            id = 5 # 21%
            base_im = 100
            importe = 21
            ws.AgregarIva(id, base_imp, importe) 
                        
            f_entrada = open(entrada,"w")
                
            if DEBUG:
                print ws.factura

            dic = ws.factura
            escribir_factura(dic, f_entrada)            
            f_entrada.close()
      
        if '/ult' in sys.argv:
            print "Consultar ultimo numero:"
            tipo_cbte = int(raw_input("Tipo de comprobante: "))
            punto_vta = int(raw_input("Punto de venta: "))
            ult_cbte = ws.CompUltimoAutorizado(tipo_cbte, punto_vta)
            print "Ultimo numero: ", ult_cbte
            depurar_xml(ws.client)
            sys.exit(0)

        if '/get' in sys.argv:
            print "Recuperar comprobante:"
            tipo_cbte = int(raw_input("Tipo de comprobante: "))
            punto_vta = int(raw_input("Punto de venta: "))
            cbte_nro = int(raw_input("Numero de comprobante: "))
            ws.CompConsultar(tipo_cbte, punto_vta, cbte_nro)

            print "FechaCbte = ", ws.FechaCbte
            print "CbteNro = ", ws.CbteNro
            print "PuntoVenta = ", ws.PuntoVenta
            print "ImpTotal =", ws.ImpTotal
            print "CAE = ", ws.CAE
            print "Vencimiento = ", ws.Vencimiento
            print "EmisionTipo = ", ws.EmisionTipo

            depurar_xml(ws.client)
            sys.exit(0)

        if '/solicitarcaea' in sys.argv:
            periodo = sys.argv[sys.argv.index("/solicitarcaea")+1]
            orden = sys.argv[sys.argv.index("/solicitarcaea")+2]

            if DEBUG: 
                print "Solicitando CAEA para periodo %s orden %s" % (periodo, orden)
            
            caea = ws.CAEASolicitar(periodo, orden)
            print "CAEA:", caea

            if ws.Errores:
                print "Errores:"
                for error in ws.Errores:
                    print error
                
            if DEBUG:
                print "Periodo:", ws.Periodo 
                print "Orden:", ws.Orden 
                print "FchVigDesde:", ws.FchVigDesde 
                print "FchVigHasta:", ws.FchVigHasta 
                print "FchTopeInf:", ws.FchTopeInf 
                print "FchProceso:", ws.FchProceso
            sys.exit(0)

        if '/consultarcaea' in sys.argv:
            periodo = raw_input("Periodo: ")
            orden = raw_input("Orden: ")

            if DEBUG: 
                print "Consultando CAEA para periodo %s orden %s" % (periodo, orden)
            
            caea = ws.CAEAConsultar(periodo, orden)
            print "CAEA:", caea

            if ws.Errores:
                print "Errores:"
                for error in ws.Errores:
                    print error
                
            if DEBUG:
                print "Periodo:", ws.Periodo 
                print "Orden:", ws.Orden 
                print "FchVigDesde:", ws.FchVigDesde 
                print "FchVigHasta:", ws.FchVigHasta 
                print "FchTopeInf:", ws.FchTopeInf 
                print "FchProceso:", ws.FchProceso
            sys.exit(0)


        f_entrada = f_salida = None
        try:
            f_entrada = open(entrada,"r")
            f_salida = open(salida,"w")
            try:
                if DEBUG: print "Autorizando usando entrada:", entrada
                autorizar(ws, f_entrada, f_salida, '/informarcaea' in sys.argv)
            except SoapFault:
                XML = True
                raise
        finally:
            if f_entrada is not None: f_entrada.close()
            if f_salida is not None: f_salida.close()
            if XML:
                depurar_xml(ws.client)
        sys.exit(0)
    
    except SoapFault,e:
        print e.faultcode, e.faultstring.encode("ascii","ignore")
        sys.exit(3)
    except Exception, e:
        print unicode(e).encode("ascii","ignore")
        if DEBUG:
            raise
        sys.exit(5)