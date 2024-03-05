import requests
from collections import OrderedDict
from bs4 import BeautifulSoup
from urllib import request
from io import BytesIO

class AsignaturaInscripcion:
    def __init__(self, **kwargs):
        self.grupo = kwargs['grupo']
        self.clave = kwargs['clave']
        self.nombre = kwargs['nombre']
        self.creditos = kwargs['creditos']
        self.ciclo = kwargs['ciclo']
        self.calificacion = kwargs['calificacion']

    def __str__(self):
        return 'Asignatura[%s (%s)]' % (self.nombre, str(self.calificacion) if self.calificacion else '-')

class Asignatura:
    def __init__(self, **kwargs):
        self.plantel = kwargs['plantel']
        self.asignatura = kwargs['asignatura']
        self.creditos = kwargs['creditos']
        self.obligatoria = kwargs['obligatoria']
        self.nombre = kwargs['nombre']
        self.calificacion = kwargs['calificacion']
        self.tipo_examen = kwargs['tipo_examen']
        self.periodo = kwargs['periodo']
        self.folio_acta = kwargs['folio_acta']
        self.grupo = kwargs['grupo']
        self.inscripciones_ordinario = kwargs['ordinario']
        self.inscripciones_extraordinario = kwargs['extraordinario']

    def __str__(self):
        return 'Asignatura[%s (%s)]' % (self.nombre, self.calificacion)

class Historial:
    def __init__(self, trayectoria, **kwargs):
        self.trayectoria = trayectoria
        self.creditos_obligatorios = kwargs['creditos_obligatorios']
        self.creditos_optativos = kwargs['creditos_optativos']
        self.total_creditos_obligatorios = kwargs['total_creditos_obligatorios']
        self.total_creditos_optativos = kwargs['total_creditos_optativos']
        self.promedio = kwargs['promedio']
        self.asignaturas_aprobadas = kwargs['asignaturas_aprobadas']
        self.asignaturas_reprobadas = kwargs['asignaturas_reprobadas']
        self.asignaturas = OrderedDict()

    def __str__(self):
        return 'Historial[%s: %s (%d%%)]' % (self.trayectoria.plantel, self.trayectoria.carrera, self.avance_creditos)

    @property
    def avance_creditos(self):
        return (self.creditos_obligatorios + self.creditos_optativos)/(self.total_creditos_obligatorios + self.total_creditos_optativos)*100

class TrayectoriaElem:
    _uri_trayectoria_elem = "https://www.dgae-siae.unam.mx/www_try.php"

    def __init__(self, alumno, siae_id, **kwargs):
        self.alumno = alumno
        self.siae_id = siae_id
        self.plantel = kwargs['plantel']
        self.carrera = kwargs['carrera']
        self.turno = kwargs['turno']
        self.plan = kwargs['plan']
        self.generacion = kwargs['generacion']
        self.ingreso = kwargs['ingreso']
        self.termino = kwargs['termino']
        self.art22 = kwargs['art22']
        self.art24 = kwargs['art24']
        self.art21 = kwargs['art21']

    def __str__(self):
        return 'TrayectoriaElem[%s: %s (%s)]' % (self.plantel, self.carrera, self.generacion)

    @property
    def historial(self) -> Historial:
        s = self.alumno.s.get(self._uri_trayectoria_elem, params={ 'cta': self.alumno.usuario, 'llave': self.siae_id, 'acc': 'hsa' })
        s2 = BeautifulSoup(s.content, 'html.parser')

        # Encabezado
        tbl_encabezado = s2.css.select('.TblBlk>tr:first-child>td>table>tr:last-child>.CellTns')
        historial_o = Historial(
            self,
            creditos_obligatorios = int(tbl_encabezado[0].select('tr:first-child>.CellTns:nth-child(2)')[0].text.strip()),
            total_creditos_obligatorios = int(tbl_encabezado[0].select('tr:first-child>.CellTns:nth-child(4)')[0].text.strip()),
            creditos_optativos = int(tbl_encabezado[0].select('tr:nth-child(2)>.CellTns:nth-child(2)')[0].text.strip()),
            total_creditos_optativos = int(tbl_encabezado[0].select('tr:nth-child(2)>.CellTns:nth-child(4)')[0].text.strip()),
            asignaturas_aprobadas = int(tbl_encabezado[1].select('tr:first-child>.CellTns:last-child')[0].text.strip()),
            asignaturas_reprobadas = int(tbl_encabezado[1].select('tr:nth-child(2)>.CellTns:last-child')[0].text.strip()),
            promedio = float(tbl_encabezado[2].select('p')[0].text.strip())
        )
        # Asignaturas
        tbl_asignaturas = s2.css.select('.TblBlk>tr:last-child>td>table>tr:not(:first-child):has(td:only-child)')
        for s in tbl_asignaturas:
            # Fila de semestre
            nom_asig = s.text.strip()
            historial_o.asignaturas[nom_asig] = []
            # Fila de asignatura
            sig = s.findNext('tr')
            while sig and not sig in tbl_asignaturas:
                tds = sig.select('td')
                historial_o.asignaturas[nom_asig].append(Asignatura(
                    plantel = tds[0].text.strip(),
                    asignatura = tds[1].text.strip(),
                    creditos = int(tds[2].text.strip()),
                    obligatoria = tds[3].text.strip() == 'OBL',
                    nombre = tds[4].text.strip(),
                    calificacion = int(tds[5].text.strip()),
                    tipo_examen = tds[6].text.strip(),
                    periodo = tds[7].text.strip(),
                    folio_acta = tds[8].text.strip(),
                    grupo = tds[9].text.strip(),
                    ordinario = int(tds[10].text.strip()) if tds[10].text.strip() else 0,
                    extraordinario = int(tds[11].text.strip()) if tds[11].text.strip() else 0
                ))
                sig = sig.findNext('tr')
        return historial_o

    @property
    def inscripcion(self) -> OrderedDict:
        s = self.alumno.s.get(self._uri_trayectoria_elem, params={ 'cta': self.alumno.usuario, 'llave': self.siae_id, 'acc': 'ins' })
        s2 = BeautifulSoup(s.content, 'html.parser')
        insc_o = OrderedDict()

        for i in s2.css.select('body>table>tr:last-child>td>table:nth-of-type(n+3)'):
            semestre = i.select('caption .badge')[0].text.strip()
            insc_o[semestre] = []
            for j in list(i.children)[5].select('td>table>tr:not(:first-child)'):
                tds = j.select('td')
                insc_o[semestre].append(AsignaturaInscripcion(
                    grupo = tds[0].text.strip(),
                    clave = tds[1].text.strip(),
                    nombre = tds[2].text.strip(),
                    creditos = int(tds[3].text.strip()),
                    ciclo = int(tds[4].text.strip()),
                    calificacion = int(tds[5].text.strip()) if tds[5].text.strip() else None
                ))
        return insc_o

class SIAE:
    _uri_gate = 'https://www.dgae-siae.unam.mx/www_gate.php'
    _uri_captcha = 'https://www.dgae-siae.unam.mx/lib/captcha.php'
    _uri_trayectoria = 'https://www.dgae-siae.unam.mx/reg_try.html'

    @property
    def _soup_trayectoria(self):
        if not hasattr(self, '_o_soup_trayectoria'):
            s = self.s.get(self._uri_trayectoria)
            self._o_soup_trayectoria = BeautifulSoup(s.content, 'html.parser')
        return self._o_soup_trayectoria
    
    @property
    def captcha(self) -> BytesIO:
        s1 = self.s.get(self._uri_gate)
        s2 = self.s.get(self._uri_captcha)
        return BytesIO(s2.content)

    def __init__(self):
        self.s = requests.session()
        self.s.headers.update({'user-agent': 'libsiae/0.1'})

    def __str__(self):
        return "Alumno[(%s) %s]" % (self.usuario, self.nombre)

    def login(self, usu: str, contra: str, captcha: str|int) -> bool:
        self.usuario = usu
        self.contrasena = contra
        self.s.post(self._uri_gate, data={
            "acc": "aut",
            "usr_logi": self.usuario,
            "usr_pass": self.contrasena,
            "captcha": str(captcha)
        })
        # Comprobar inicio de sesión exitoso
        try:
            a = self.nombre
            return True
        except:
            del self._o_soup_trayectoria
            return False

    @property
    def nombre(self) -> str:
        return self._soup_trayectoria.css.select('#frmSIAE table .TblBlk')[0].select('tr:nth-child(2)>.CellDat')[0].text.strip()

    @property
    def fotografia(self) -> BytesIO:
        img = self._soup_trayectoria.css.select('.foto_alumno')
        if len(img):
            return request.urlopen(img[0]['src'])

    @property
    def trayectoria(self) -> list:
        lista = []
        s = self._soup_trayectoria.css.select('#frmSIAE table .TblBlk')[1].select('tr:has([name=llave])')
        for i in s:
            tds = i.select('td')
            lista.append(TrayectoriaElem(
                self,
                # Formato: carrera,plan,^grado,^,^plantel,^,^generacion,ingreso,^,facultad
                list(tds[0].children)[0].attrs['value'],
                plantel = tds[1].text.strip(),
                carrera = tds[2].text.strip(),
                turno = tds[3].text.strip(),
                plan = tds[4].text.strip(),
                generacion = tds[5].text.strip(),
                ingreso = tds[6].text.strip(),
                termino = tds[7].text.strip(),
                art22 = tds[8].text.strip(),
                art24 = tds[9].text.strip(),
                art21 = tds[10].text.strip()
            ))
        return lista
