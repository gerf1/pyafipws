[{'components': [{'name': 'lblWebservice',
                  'pos': (18, 10),
                  'text': u'Webservice:',
                  'type': 'Label'},
                 {'items': [u'wsfe', u'wsfev1', u'wsfexv1'],
                  'name': 'cboWebservice',
                  'pos': (102, 5),
                  'size': (89, -1),
                  'type': 'ComboBox'},
                 {'label': u'Marcar Todo',
                  'name': 'btnMarcarTodo',
                  'pos': (297, 163),
                  'tooltip': u'Seleccionar todas las facturas',
                  'type': 'Button'},
                 {'label': u'Autorizar Lote',
                  'name': 'btnAutorizarLote',
                  'pos': (188, 163),
                  'tooltip': u'Obtener CAE para todas las facturas',
                  'type': 'Button'},
                 {'label': u'Previsualizar',
                  'name': 'btnPrevisualizar',
                  'pos': (395, 163),
                  'type': 'Button'},
                 {'label': u'Autenticar',
                  'name': 'btnAutenticar',
                  'pos': (20, 163),
                  'tooltip': u'Iniciar Sesin en la AFIP',
                  'type': 'Button'},
                 {'font': {'face': u'Sans',
                           'family': 'sans serif',
                           'size': 8},
                  'name': 'txtEstado',
                  'pos': (20, 243),
                  'size': (534, 212),
                  'type': 'TextBox',
                  'value': u'\n'},
                 {'name': 'lblProgreso',
                  'pos': (20, 194),
                  'text': u'Progreso:',
                  'type': 'Label'},
                 {'name': 'lblEstado',
                  'pos': (22, 219),
                  'text': u'Estado:',
                  'type': 'Label'},
                 {'label': u'Enviar',
                  'name': 'btnEnviar',
                  'pos': (490, 163),
                  'size': (60, -1),
                  'tooltip': u'Generar y enviar mails',
                  'type': 'Button'},
                 {'editable': False,
                  'name': 'txtArchivo',
                  'pos': (260, 5),
                  'size': (300, -1),
                  'type': 'TextBox',
                  'value': u'facturas.csv'},
                 {'name': 'lblArchivo',
                  'pos': (195, 10),
                  'text': u'Archivo:',
                  'type': 'Label'},
                 {'label': u'Autorizar',
                  'name': 'btnAutorizar',
                  'pos': (104, 163),
                  'tooltip': u'Obtener CAE por cada factura',
                  'type': 'Button'},
                 {'bgcolor': (255, 255, 255, 255),
                  'columnHeadings': [],
                  'font': {'face': u'Tahoma',
                           'family': 'sans serif',
                           'size': 8},
                  'items': [],
                  'maxColumns': 1000,
                  'name': 'lvwListado',
                  'pos': (18, 53),
                  'rules': 1,
                  'size': (537, 106),
                  'type': 'ListView'},
                 {'name': 'lblFacturas',
                  'pos': (18, 35),
                  'size': (117, -1),
                  'text': u'Facturas:',
                  'type': 'Label'},
                 {'bgcolor': (209, 194, 182, 255),
                  'layout': 'horizontal',
                  'max': 100,
                  'name': 'pbProgreso',
                  'pos': (89, 195),
                  'size': (477, 16),
                  'type': 'Gauge',
                  'value': 0}],
  'menubar': [{'items': [{'label': u'Abrir',
                          'name': 'menuArchivoAbrir',
                          'type': 'MenuItem'},
                         {'label': u'ReCargar',
                          'name': 'menuArchivoCargar',
                          'type': 'MenuItem'},
                         {'label': u'Guardar',
                          'name': 'menuArchivoGuardar',
                          'type': 'MenuItem'}],
               'label': u'Archivo',
               'name': 'menuArchivo',
               'type': 'Menu'},
              {'items': [{'label': u'Estado Servidores (Dummy)',
                          'name': 'menuConsultasDummy',
                          'type': 'MenuItem'},
                         {'label': u'\xdalt. Cbte.',
                          'name': 'menuConsultasLastCBTE',
                          'type': 'MenuItem'},
                         {'label': u'\xdalt. ID',
                          'name': 'menuConsultasLastID',
                          'type': 'MenuItem'},
                         {'label': u'Recuperar CAE',
                          'name': 'menuConsultasGetCAE',
                          'type': 'MenuItem'}],
               'label': u'Consultas',
               'name': 'menuConsultas',
               'type': 'Menu'},
              {'items': [{'label': u'Instructivo',
                          'name': 'menuAyudaInstructivo',
                          'type': 'MenuItem'},
                         {'label': u'Acerca de',
                          'name': 'menuAyudaAcercaDe',
                          'type': 'MenuItem'},
                         {'label': u'Limpiar estado',
                          'name': 'menuAyudaLimpiar',
                          'type': 'MenuItem'},
                         {'label': u'Mensajes XML',
                          'name': 'menuAyudaMensajesXML',
                          'type': 'MenuItem'},
                         {'label': u'Ver/Ocultar Estado',
                          'name': 'menuAyudaVerEstado',
                          'type': 'MenuItem'},
                         {'label': u'Ver Configuraci\xf3n',
                          'name': 'menuAyudaVerConfiguracion',
                          'type': 'MenuItem'}],
               'label': u'Ayuda',
               'name': 'menuAyuda',
               'type': 'Menu'}],
  'name': 'bgTemplate',
  'size': (592, 265),
  'title': u'Aplicativo Factura Electr\xf3nica (PyRece)',
  'type': 'Window'}]
