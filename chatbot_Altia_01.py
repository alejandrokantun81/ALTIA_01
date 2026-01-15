import streamlit as st
from openai import OpenAI
import os

# ---------------------------------------------------------
# 1. BASE DE CONOCIMIENTO MAESTRA DE ALTIUS COBAY
# ---------------------------------------------------------
DATOS_RAG = [
    # =========================================================================
    # BLOQUE 1: REGLAMENTO INTERIOR DE TRABAJO
    # =========================================================================
    {
        "id": "rit_01",
        "metadata": { "sección": "Preámbulo y Cap I (Arts. 1-2)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Reglamento Interior de Trabajo del Colegio de Bachilleres del Estado de Yucatán (COBAY). Fundamentado en la Ley del COBAY. Cap I. Art 1: Observancia obligatoria. Art 2 (Definiciones): 'Adscripción' (lugar de servicio), 'Alumno', 'Centros EMSAD', 'Contrato Colectivo', 'Jornada de trabajo' (tiempo a disposición). Tipos de trabajador: 'Docente', 'Administrativo', 'Técnico', 'Manual'."
    },
    {
        "id": "rit_02",
        "metadata": { "sección": "Cap II: Relaciones Individuales (Arts. 3-5)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Cap II. Art 3: Contrato debe tener datos, duración, categoría, salario. Art 4: Terminación según art 53 LFT. Art 5 (Rescisión sin responsabilidad patrón): Certificados falsos, violencia, pedir dádivas, alterar documentos, embriaguez/drogas, portar armas."
    },
    {
        "id": "rit_03",
        "metadata": { "sección": "Cap II: Rescisión y Terminación (Arts. 5-8)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Continuación Art 5: Sustraer equipos, daños, acoso sexual, faltar >3 días en 30 días, negarse a evaluaciones, prisión. Art 6: Rescisión por trabajador (Art 51 LFT). Art 7: Renuncia con finiquito previo no adeudo. Pago en 30 días. Art 8: Constancias de no adeudo en 5 días."
    },
    {
        "id": "rit_04",
        "metadata": { "sección": "Cap III: Ingreso y IV: Nombramientos (Arts. 9-13)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Cap III. Art 9: Requisitos: Mexicano (o extranjero con permiso), aprobar evaluación. Docentes por Ley Servicio Profesional. Art 10: Documentos (CV, Título, Cédula, Antecedentes no penales, etc). Art 11: Prohibido 'meritorios'. Cap IV. Art 12: Nombramientos por escrito (Dir. Gral). Art 13: Servicio estricto al contrato."
    },
    {
        "id": "rit_05",
        "metadata": { "sección": "Cap V: Movimientos y VI: Jornada (Arts. 14-20)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Cap V. Altas, Movimientos, Promociones. Cap VI. Art 18-19: Jornadas: Completa (7h o 8h docentes), Tres cuartos (5-7h), Media (3.5-5h), Por horas clase. Art 20: Servicio fuera de adscripción cuenta desde el punto de concentración."
    },
    {
        "id": "rit_06",
        "metadata": { "sección": "Cap VI: Horarios y Registro (Arts. 21-26)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 21: Horarios según necesidades. Art 22: 30 min alimentos en continuo. Art 24-26: Registro obligatorio (lector, reloj, lista). Si falla, avisar a RH y usar libreta."
    },
    {
        "id": "rit_07",
        "metadata": { "sección": "Cap VI: Tolerancias y Retardos (Arts. 27-30)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 28 Tolerancias: Admin/Docente jornada: 20 min. Docente horas: 10 min (1ra hora). 2 tolerancias = 1 retardo. Art 29-30 Retardos: Admin (min 21-30), Docente horas (min 11-20). 3 retardos = 1 falta injustificada."
    },
    {
        "id": "rit_08",
        "metadata": { "sección": "Cap VI: Faltas y Descuentos (Arts. 31-33)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 31: Falta si llega después de tolerancia/retardo o no checa. Art 33 Faltas injustificadas (no pago): Sin permiso, 4 faltas en 30 días, salir antes, abandonar labores."
    },
    {
        "id": "rit_09",
        "metadata": { "sección": "Cap VI: Justificaciones y Estímulos (Arts. 34-36)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 34: Max 3 justificaciones/semestre. Art 35 Estímulo Puntualidad: Base/plaza con 90% asistencia. 7.5 días salario/semestre. Art 36 Días Económicos: 9 al año (base/plaza 1 año antigüedad). Solicitar 2 días antes. No usados se pagan en enero."
    },
    {
        "id": "rit_10",
        "metadata": { "sección": "Cap VII: Lugar y Permutas (Arts. 37-41)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 37: Cambio adscripción por reorganización o necesidad sin responsabilidad patrón. Art 39 Permuta: Intercambio mismo puesto/sueldo. Art 41: Esperar 2 años para nueva permuta."
    },
    {
        "id": "rit_11",
        "metadata": { "sección": "Cap VII: Mantenimiento y VIII: Pagos (Arts. 42-48)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 42: Limpieza y cuidado. Cap VIII. Art 45: Pago días 15 y último. Art 48: Deducciones solo por ley (Art 110 LFT)."
    },
    {
        "id": "rit_12",
        "metadata": { "sección": "Cap IX: Descansos y Vacaciones (Arts. 49-53)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 49: 5 días trabajo x 2 descanso. Art 51 Vacaciones: 2 periodos de 10 días hábiles (1 año antigüedad). Art 52 Prima: 12 días/semestre (Base), 6 días/semestre (Contrato)."
    },
    {
        "id": "rit_13",
        "metadata": { "sección": "Cap X: Aguinaldo y XI: Licencias (Arts. 54-55)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 54 Aguinaldo: 40 días (Base), 20 días (Contrato). Pago antes 20 dic. Cap XI Licencias Sin Goce: Hijos <1 año (6 m), Asuntos particulares (6 m, req 2 años ant.), Cargos elección."
    },
    {
        "id": "rit_14",
        "metadata": { "sección": "Cap XI: Licencias con Goce (Arts. 56-57)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 56 Con Goce (Base): Gravidez (90 días), Lactancia (2 reposos 30 min o reducción), Paternidad/Adopción (5 días). Art 57: Solicitud escrita a Dir Gral."
    },
    {
        "id": "rit_15",
        "metadata": { "sección": "Cap XII: Obligaciones (Art. 58)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 58: Cumplir normas, respeto alumnos/compañeros, no violencia, cuidar materiales, confidencialidad, no propaganda, actualizar datos."
    },
    {
        "id": "rit_16",
        "metadata": { "sección": "Cap XIII: Prohibiciones (Art. 59)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 59: Prohibido: Gratificaciones, faltar, abandonar, falsificar, uso personal bienes, embriaguez, armas, acoso sexual, alterar disciplina."
    },
    {
        "id": "rit_17",
        "metadata": { "sección": "Cap XIV: Obligaciones COBAY y XV: Seguridad (Arts. 60-64)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 60 COBAY: No discriminar, pagar oportuno. Cap XV: Seguridad e higiene responsabilidad COBAY. Trabajador debe avisar accidentes en 48h."
    },
    {
        "id": "rit_18",
        "metadata": { "sección": "Cap XV: Accidentes (Arts. 65-69)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 66: IMSS califica riesgos. Art 68: Justificación solo con incapacidad IMSS (48h). Art 69: Acta circunstanciada inmediata."
    },
    {
        "id": "rit_19",
        "metadata": { "sección": "Cap XVI: Capacitación y Ascensos (Arts. 70-77)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 70: Capacitación obligatoria (Comisión Mixta). Art 74: Ascensos por preparación, antigüedad y eficiencia."
    },
    {
        "id": "rit_20",
        "metadata": { "sección": "Cap XVII: Sanciones (Arts. 78-80)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 78: Extrañamiento, Suspensión (1-8 días), Rescisión. Art 79 Extrañamiento: Falta respeto, descuido, etc."
    },
    {
        "id": "rit_21",
        "metadata": { "sección": "Cap XVII: Suspensiones y Proceso (Arts. 81-86)", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 81 Suspensión: Daños, reincidencia, etc. Art 82: Acta administrativa con audiencia. Prescribe en 30 días."
    },
    {
        "id": "rit_22",
        "metadata": { "sección": "Cap XVIII, XIX y Transitorios", "tipo_documento": "Reglamento Interior de Trabajo" },
        "contenido": "Art 88: Incompatibilidad de dos plazas. Vigencia desde 24 abril 2014."
    },

    # =========================================================================
    # BLOQUE 2: REGLAMENTO ACADÉMICO
    # =========================================================================
    {
        "id": "acad_01",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título I: Generalidades y Objetivos (Arts. 1-3)" },
        "contenido": "REGLAMENTO ACADÉMICO COBAY. TÍTULO PRIMERO. Art 1: Cobay es organismo público descentralizado. Art 2: Imparte Bachillerato General escolarizado y EMSAD. Objetivos: Fortalecer capacidad intelectual, educación de calidad, competencias y TIC. Art 3: Facultades: Equivalencias, incorporar escuelas, promover cultura/deporte."
    },
    {
        "id": "acad_02",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título I: Definiciones y Modalidades (Arts. 4-7)" },
        "contenido": "Art 4 Definiciones: Alumno (con matrícula vigente), Actividades paraescolares, Centro EMSAD, Personal Académico, Planteles. Art 6 Modalidades: I. Escolarizada. II. EMSAD. Duración máxima del bachillerato: 10 semestres. Art 7: Observancia obligatoria."
    },
    {
        "id": "acad_03",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título I Cap II: Plan de Estudios (Arts. 8-12)" },
        "contenido": "Art 8 Plan de Estudios: Matemáticas, Ciencias Experimentales, Comunicación, Ciencias Sociales, Humanidades. Art 9 Componentes: Básico, Propedéutico (5to-6to sem) y Formación para Trabajo (3ro-6to sem). Art 11: Alumno elige capacitación en 1ra semana de 3er semestre."
    },
    {
        "id": "acad_04",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap I-II: Categorías e Ingreso (Arts. 13-16)" },
        "contenido": "Art 13 Categorías: Regular (sin adeudos), Irregular (adeuda max 3 UAC), Repetidor (2da vez en mismo semestre, reprobó 4+). Art 14 Ingreso: Solicitud, Certificado secundaria, Acta nacimiento (max 17 años), Fotos, CURP, Examen."
    },
    {
        "id": "acad_05",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap II: Inscripción (Arts. 17-25)" },
        "contenido": "Art 19 Inscripción 1er sem: Seleccionado en examen, entregar documentos y cubrir cuotas. Art 22 Extemporánea: Max 20 días hábiles. Art 24 Certificado secundaria limite 15 oct. Art 25: Prohibidos alumnos oyentes."
    },
    {
        "id": "acad_06",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap II: Reinscripción y Cambios (Arts. 26-30)" },
        "contenido": "Art 26: Reinscripción semestral. Recursar mismo semestre solo una vez. Art 28 Cambio plantel: Una vez por ciclo, sujeto a cupo y autorización DCE. Art 30: Inscripción con estudios parciales requiere equivalencia."
    },
    {
        "id": "acad_07",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap III: Equivalencia y Revalidación (Arts. 31-38)" },
        "contenido": "Art 32: Equivalencia por semestre completo si acredita todo (solo 2º-5º sem). Art 33: Dictamen por UAC si es incompleto. Art 36: Trámite ante DCE, validez un semestre."
    },
    {
        "id": "acad_08",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap IV: Evaluación y Acreditación (Arts. 39-44)" },
        "contenido": "Art 40 Mínimo aprobatorio: 70 puntos. Art 41 Ordinaria: Dos parciales (70% formativa, 30% sumativa). Promedio parciales = 70% final. Examen ordinario = 30% final. Exenta ordinario con 100 en parciales. Art 42: Req 90% asistencia para derecho a evaluación."
    },
    {
        "id": "acad_09",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap IV-V: Promoción y Recuperación (Arts. 45-51)" },
        "contenido": "Art 47 Promoción: No adeudar >3 UAC, no exceder 10 semestres. Art 49: Reprobar 4+ UAC tras recuperación = Repetidor (baja temporal). Art 51 Recuperación: al concluir ordinario (1-4 UAC reprobadas)."
    },
    {
        "id": "acad_10",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap V: Evaluación Extraordinaria y Especial (Arts. 52-57)" },
        "contenido": "Art 53 Irregulares (max 3 UAC pendientes) van a Extraordinario (hasta 2 veces misma UAC). Art 54 Evaluación Especial: Última oportunidad si debe 1 sola UAC tras extra. Art 56: No repetir mismo semestre >1 vez."
    },
    {
        "id": "acad_11",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap VI: Revisión Académica (Arts. 58-62)" },
        "contenido": "Art 59 Revisión calificación: Solicitud en 3 días hábiles. Art 62 Renuncia calificaciones: Para mejorar promedio (max 3 UAC). Req ser regular. Calificación de extraordinario es definitiva."
    },
    {
        "id": "acad_12",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap VII: Bajas (Arts. 63-69)" },
        "contenido": "Art 63 Bajas: Temporal y Definitiva. Art 64 Temporal: Max 2 semestres. Causas: Solicitud, reprobar 4+, sanción. Art 67 Deserción: Inasistencia 15 días naturales."
    },
    {
        "id": "acad_13",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap VII-VIII: Baja Definitiva y Certificación (Arts. 70-77)" },
        "contenido": "Art 71 Baja Definitiva: Solicitud, rebasar 10 semestres, documentos falsos, agotar oportunidades, faltas graves. Art 76 Certificado terminación: Acredita plan completo."
    },
    {
        "id": "acad_14",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap IX: Derechos (Art. 78)" },
        "contenido": "Art 78 Derechos Alumnos: Educación calidad, trato digno, credencial, becas, seguro facultativo, ser representante, revisión calificaciones."
    },
    {
        "id": "acad_15",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap IX: Obligaciones (Art. 79)" },
        "contenido": "Art 79 Obligaciones: Cumplir normas, enaltecer Cobay, uniforme, disciplina. Prohibido: Suspender labores, falsificar, violencia, drogas, armas, dañar bienes."
    },
    {
        "id": "acad_16",
        "metadata": { "tipo_documento": "Reglamento Académico", "sección": "Título II Cap IX y Transitorios: Sanciones (Arts. 80-82)" },
        "contenido": "Art 80 Sanciones: Amonestación, Suspensión (max 3 días), Baja temporal, Baja definitiva. Art 82: Baja definitiva por indisciplina grave requiere dictamen Dir. Académica. Vigencia desde 2017."
    },

    # =========================================================================
    # BLOQUE 3: CONTRATO COLECTIVO DE TRABAJO
    # =========================================================================
    {
        "id": "cct_01",
        "metadata": { "sección": "Aprobación y Votación 2024", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "CFCRL 30 abril 2024: Aprobación Convenio Revisión CCT-01/2020 entre STCBEY y COBAY. Consulta 20 marzo 2024: 1515 votos emitidos, 885 a favor (58%). Cumple Art 390 Ter LFT. Se ordena registro."
    },
    {
        "id": "cct_02",
        "metadata": { "sección": "Definiciones (I-XIII)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "CCT-01/2020 COBAY-STCBEY. Definiciones: I. COBAY. II. STCBEY (Sindicato titular). IV. Trabajador Activo. VIII. Salario. IX. Salario Tabulado. X. Tabulador. XI. Adscripción. XIII. Representantes (Comité Ejecutivo)."
    },
    {
        "id": "cct_03",
        "metadata": { "sección": "Cap I: Disposiciones (Clausulas 1-5)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 1: Regula condiciones base/plaza. Excluye confianza (salvo seg. social/aguinaldo). Cláusula 2: COBAY reconoce a STCBEY como titular del CCT. Cláusula 3: Leyes aplicables (CCT, Estatuto, LFT, Ley Trabajadores Estado Yucatán)."
    },
    {
        "id": "cct_04",
        "metadata": { "sección": "Cap II-III: Revisión (Clausulas 6-13)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 6: Revisión salarial anual, integral cada 2 años. Cláusula 10: Ingreso sujeto a Ley Sistema Carrera Maestras. Cláusula 11: Preferencia mexicanos y sindicalizados. Cláusula 13: COBAY provee material de calidad."
    },
    {
        "id": "cct_05",
        "metadata": { "sección": "Cap IV-V: Derechos y Clasificación (Clausulas 14-17)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 14: Derechos irrenunciables. Cláusula 16: Reubicación por reforma educativa o supresión de plaza (indemnización si no hay reubicación). Transferencias voluntarias o necesarias con 15 días aviso. Cláusula 17: Reclasificación no debe perjudicar salario."
    },
    {
        "id": "cct_06",
        "metadata": { "sección": "Cap VI-VII: Jornada y Salario (Clausulas 18-22)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 18: Jornada Admin (35h/sem), Docente (40h, 30h, 20h o por hora). Vigilantes acumulada fin semana. Cláusula 19: 5 días labor x 2 descanso. Cláusula 20: Salario según tabulador autorizado presupuesto egresos."
    },
    {
        "id": "cct_07",
        "metadata": { "sección": "Cap VII: Pagos y Descuentos (Clausulas 23-25)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 23: Pago días 15 y 30. Cláusula 25 Descuentos: Deudas COBAY/ISSTEY, Cuotas sindicales, Pensión alimenticia, Caja ahorro STCBEY."
    },
    {
        "id": "cct_08",
        "metadata": { "sección": "Cap VIII-IX: Vacaciones y Licencias (Clausulas 26-29)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 26: 2 periodos vacacionales 10 días hábiles. Manuales antes del periodo escolar. Cláusula 28: Licencia sin goce (tras 2 años antigüedad): Hasta 6 meses renovables. Reincorporación misma condición."
    },
    {
        "id": "cct_09",
        "metadata": { "sección": "Cap IX: Gravidez y Cargos (Clausulas 30-32)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 32 Gravidez: 120 días sueldo íntegro. Discapacidad hijo (+8 sem). Adopción (8 sem). Lactancia/Complicaciones (+10 días). Prórroga si coincide con vacaciones."
    },
    {
        "id": "cct_10",
        "metadata": { "sección": "Cap X: Comisiones Mixtas (Clausulas 33-39)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 33 Comisiones Mixtas (STCBEY-COBAY): Seguridad e Higiene, Capacitación, Antigüedades, Reglamento Interior."
    },
    {
        "id": "cct_11",
        "metadata": { "sección": "Cap XI-XII: Servicios Médicos y Sanciones (Clausulas 40-44)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 40: Servicio Médico ISSTEY/IMSS (cubre familia). Cláusula 41: Justificantes IMSS. Cláusula 44 Sanciones: Extrañamiento, Acta, Suspensión (max 8 días), Rescisión."
    },
    {
        "id": "cct_12",
        "metadata": { "sección": "Cap XIII-XIV: Obligaciones COBAY (Clausulas 45-50)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 45: Preferencia propuesta STCBEY para vacantes. Cláusula 48: Entrega CCT. Cláusula 50: Trato con representantes STCBEY."
    },
    {
        "id": "cct_13",
        "metadata": { "sección": "Prestaciones Económicas I (Clausulas 51-58)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 52 Despensa: Plaza $1,380.50 ($2,761 dic), Base $34.50/hr ($69 dic). Cláusula 53 Aguinaldo: 40 días tabulado. Cláusula 54 Vale Pavo 8kg. Cláusula 55-56 Apoyo convivios ($150). Cláusula 57 Prima Vacacional: 12 días/periodo. Cláusula 58 Ajuste Calendario: 5 días salario en dic."
    },
    {
        "id": "cct_14",
        "metadata": { "sección": "Prestaciones Económicas II (Clausulas 59-63)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 59 Días Económicos: 9/año. No usados se pagan enero (12 días). Cláusula 60 Puntualidad: 7.5 días/semestre (90% asistencia). Cláusula 61 Prima Antigüedad: 1.5% salario/año desde 15 años. Cláusula 62 Estímulo Antigüedad: $2,000 (10, 20, 30 años). Cláusula 63 Eficiencia (Tabla)."
    },
    {
        "id": "cct_15",
        "metadata": { "sección": "Ayudas Sociales (Clausulas 64-69)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 64 Titulación: $5,000. Cláusula 65 Útiles: $300-$500/hijo. Cláusula 66-67 Lentes/Ortopédicos: $2,500/$2,150 anual. Cláusula 68 Seguro Vida: 40 meses. Cláusula 69 Defunción: $17,000."
    },
    {
        "id": "cct_16",
        "metadata": { "sección": "Días y Apoyos Docentes (Clausulas 70-76)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 70: Pago extra 24 abril y 15 mayo. Cláusula 72 Material Didáctico. Cláusula 73 Productividad (18.53%). Cláusula 74 Superación Académica (titulados). Cláusula 76 Libros: $600 anual."
    },
    {
        "id": "cct_17",
        "metadata": { "sección": "Apoyos Familiares (Clausulas 77-90)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 77 Exención inscripción hijos. Cláusula 78 Canastilla $1,500. Cláusula 79 Guardería $588/mes. Cláusula 80 Prima dominical. Cláusula 88 Paternidad: 5 días. Cláusula 89 Enfermedad familiar: 6 días/año. Cláusula 90 Licencia cuidados <1 año (6-12 meses sin goce)."
    },
    {
        "id": "cct_18",
        "metadata": { "sección": "Días Personales y Tabulador (Clausulas 91-Final)", "tipo_documento": "Contrato Colectivo de Trabajo" },
        "contenido": "Cláusula 91 Uniformes. Cláusula 92-95 Descansos: Cumpleaños, Día Madre/Padre, Luto (3 días directo, 2 indirecto). Anexo Tabulador: Técnico ($7.5k-11k), Vigilante ($8.4k), Profesor CB I ($435/hr)."
    },

    # =========================================================================
    # BLOQUE 4: DIRECTORIO INSTITUCIONAL
    # =========================================================================
    {
        "id": "dir_01",
        "metadata": { "sección": "Dirección General y Staff", "tipo_documento": "Directorio Institucional" },
        "contenido": """
        DIRECTORIO DE AUTORIDADES DEL COBAY:
         
        1. DIRECCIÓN GENERAL
           - Titular: Mtro. Didier Manuel De Jesús Barrera Novelo (Director General).
           - Dirección: Calle 34 núm. 420-B x 35, Col. López Mateos, Mérida.
           - Teléfono: (999) 611 8690 Ext. 28051 y 28052.
         
        2. UNIDAD DE VINCULACIÓN
           - Titular: Ing. Manuel Alberto Bonilla Campo (Jefe de Unidad).
           - Teléfono: Ext. 28091.
         
        3. COMUNICACIÓN SOCIAL
           - Titular: Lic. Martín Rodrigo Kauil Conde (Jefe de Departamento).
           - Teléfono: Ext. 28007.
         
        4. RELACIONES PÚBLICAS
           - Titular: Lic. Oswaldo Cardeña Medina (Jefe de Departamento).
           - Teléfono: Ext. 28007.
         
        5. DIRECCIÓN JURÍDICA
           - Titular: Mtro. David Alejandro Patrón Bianchi (Director Jurídico).
           - Teléfono: Ext. 28044 y 28045.
           - Asuntos Contenciosos: Lic. Alfonso Arturo Orozco Araiza (Jefe Depto). Tel: Ext. 608 / Cel: 9991678554.
           - Asuntos Mixtos: Lic. Julio César Rodríguez (Jefe Depto). Tel: Ext. 605 / Cel: 9991678554.
           - Unidad de Transparencia: Lic. Gabriela Margarita Montejo Diaz. Tel: Ext. 605 / Cel: 9991678554.
        """
    },
    {
        "id": "dir_02",
        "metadata": { "sección": "Dirección Administrativa y Planeación", "tipo_documento": "Directorio Institucional" },
        "contenido": """
        6. DIRECCIÓN ADMINISTRATIVA
           - Titular: C.P. Martha Cecilia Dorantes Caballero (Directora Administrativa).
           - Teléfono: Ext. 608 / Cel: 9991678554.
           - Subdirección de Finanzas: C.P. Daniel Gallardo Colli. Tel: Ext. 606 / Cel: 9991678554.
           - Recursos Humanos: Lic. Lizbeth Beatríz García Pérez. Tel: Ext. 28015.
           - Recursos Materiales: Mtra. Maira Alejandra Alcocer Pulido. Tel: (999) 611 8690 / Cel: 9991678553.
           - Informática: Lic. Leydi Del Socorro Cobá. Tel: Ext. 28022.
           - Servicios Generales: Mtro. José Carlos Brito Díaz. Tel: (999) 611 8690 / Cel: 9999254377.
           - Unidad de Control y Evaluación (Interna): Mtro. Leobardo Medina Xix. Tel: Ext. 602 / Cel: 9991678554.
           - Supervisión Zona 01: Lic. Javier Arcangel May Meléndez (Ext. 28046).
           - Supervisión Zona (General): Lic. José Dolores Chay Cauich (Ext. 28046).
           - Supervisión Zona 03: Mtro. Luis Enrique Alamilla Herrera (Ext. 28046).

        7. DIRECCIÓN TÉCNICA Y PLANEACIÓN
           - Titular: Mtra. Mariela Elizabeth Mena Godoy.
           - Teléfono: Ext. 28040.
           - Presupuesto: C.P. Cristina Isabel Sánchez López. Tel: Ext. 606 / Cel: 9991678554.
           - Estadísticas: Ing. Beatriz De Fátima Arceo Medina. Tel: Ext. 606 / Cel: 9991678554.
           - Estudios y Proyectos: Arqto. Antonio Morales Balderas. Tel: Ext. 28091.
        """
    },
    {
        "id": "dir_03",
        "metadata": { "sección": "Dirección Académica", "tipo_documento": "Directorio Institucional" },
        "contenido": """
        8. DIRECCIÓN ACADÉMICA
           - Director: Dr. Cristian Miguel Sosa Molina.
           - Teléfono: Ext. 28025 y 28026.
           
           - Subdirector Académico: Dr. Manuel Alejandro Kantún Ramírez.
           - Teléfono: Ext. 28026.
           
           - Control Escolar: Lic. Ileana Del Carmen Rodríguez Quintal. Tel: Ext. 28036.
           - Actualización y Formación Docente: Lic. Tania Beatríz Figueroa Chan. Tel: Ext. 28028.
           - Servicios Académicos: Mtro. Marco Antonio Turriza Chan. Tel: Ext. 28027.
           - Orientación, Laboratorios y Bibliotecas: Mtro. Javier Concha Bastarrachea. Tel: Ext. 28031.
           - Actividades Cívicas, Culturales y Deportivas: Lic. Jorge Abel Jiménez Aguilar. Tel: Ext. 28034.
           - Coordinación EMSAD: Laet. Minelia Soberanis Herrera. Tel: Ext. 28039.
        """
    },

    # =========================================================================
    # BLOQUE 5: ELIMINADO (Calendario Escolar)
    # =========================================================================

    # =========================================================================
    # BLOQUE 6: PLANTELES Y MATRÍCULA 2025-B
    # =========================================================================
    {
        "id": "mat_01",
        "metadata": { "sección": "Estadísticas Generales y Planteles 1-30", "tipo_documento": "Matrícula 2025-B" },
        "contenido": """
        RESUMEN ESTADÍSTICO 2025-B:
        - Total Planteles: 72
        - Matrícula Global: 27,704 alumnos.
        - Desglose: 1º Semestre (10,575), 3º Semestre (8,743), 5º Semestre (8,386).

        DETALLE PLANTELES (ID 1-30):
        1. ABALA: 103 alumnos (1º:38, 3º:34, 5º:31).
        2. ACANCEH: 435 alumnos (1º:173, 3º:130, 5º:132).
        3. AKIL: 337 alumnos (1º:150, 3º:85, 5º:102).
        4. BACA: 365 alumnos (1º:135, 3º:111, 5º:119).
        6. BUCTZOTZ: 262 alumnos (1º:94, 3º:65, 5º:103).
        5. CACALCHEN: 270 alumnos (1º:103, 3º:86, 5º:81).
        7. CALOTMUL: 109 alumnos (1º:46, 3º:32, 5º:31).
        8. CAUCEL: 661 alumnos (1º:233, 3º:213, 5º:215).
        9. CENOTILLO: 115 alumnos (1º:43, 3º:38, 5º:34).
        10. CELESTUN: 208 alumnos (1º:74, 3º:61, 5º:73).
        11. CENOTILLO (2): 115 alumnos (1º:43, 3º:38, 5º:34).
        12. CHACSINKIN: 120 alumnos (1º:43, 3º:39, 5º:38).
        13. CHANKOM: 114 alumnos (1º:42, 3º:34, 5º:38).
        14. CHAPAB: 113 alumnos (1º:48, 3º:32, 5º:33).
        15. CHEMAX: 721 alumnos (1º:285, 3º:232, 5º:204).
        16. CHENKU: 1424 alumnos (1º:480, 3º:465, 5º:479).
        17. CHICHIMILA: 249 alumnos (1º:107, 3º:79, 5º:63).
        18. CHICXULUB PUEBLO: 161 alumnos (1º:74, 3º:46, 5º:41).
        19. CHOCHOLA: 163 alumnos (1º:63, 3º:45, 5º:55).
        20. CHUMAYEL: 144 alumnos (1º:57, 3º:38, 5º:49).
        21. DZAN: 187 alumnos (1º:73, 3º:58, 5º:56).
        22. DZEMUL: 127 alumnos (1º:46, 3º:33, 5º:48).
        23. DZIDZANTUN: 260 alumnos (1º:93, 3º:82, 5º:85).
        24. DZILAM GONZALEZ: 208 alumnos (1º:76, 3º:65, 5º:67).
        25. DZITAS: 154 alumnos (1º:65, 3º:47, 5º:42).
        26. ESPITA: 451 alumnos (1º:185, 3º:145, 5º:121).
        27. HALACHO: 477 alumnos (1º:182, 3º:156, 5º:139).
        28. HOCTUN: 248 alumnos (1º:98, 3º:77, 5º:73).
        29. HOMUN: 294 alumnos (1º:113, 3º:99, 5º:82).
        30. HUHI: 191 alumnos (1º:73, 3º:55, 5º:63).
        """
    },
    {
        "id": "mat_02",
        "metadata": { "sección": "Planteles 31-60", "tipo_documento": "Matrícula 2025-B" },
        "contenido": """
        DETALLE PLANTELES (ID 31-60):
        31. HUNUCMA: 696 alumnos (1º:293, 3º:218, 5º:185).
        32. IXIL: 129 alumnos (1º:55, 3º:40, 5º:34).
        33. KANNASIN: 1016 alumnos (1º:456, 3º:290, 5º:270).
        34. KANTUNIL: 149 alumnos (1º:52, 3º:54, 5º:43).
        35. KINCHIL: 267 alumnos (1º:110, 3º:80, 5º:77).
        36. LOBAIN: 576 alumnos (1º:186, 3º:191, 5º:199).
        37. MANI: 179 alumnos (1º:61, 3º:57, 5º:61).
        38. MAXCANU: 452 alumnos (1º:169, 3º:139, 5º:144).
        39. MAYAPAN: 126 alumnos (1º:50, 3º:39, 5º:37).
        40. MERIDA-NTE: 1120 alumnos (1º:348, 3º:366, 5º:406).
        41. MOCOCHA: 107 alumnos (1º:45, 3º:33, 5º:29).
        42. MOTUL: 519 alumnos (1º:195, 3º:178, 5º:146).
        43. MUNA: 398 alumnos (1º:146, 3º:126, 5º:126).
        44. OPICHEN: 233 alumnos (1º:91, 3º:68, 5º:74).
        45. OXKUTZCAB: 552 alumnos (1º:218, 3º:176, 5º:158).
        46. PANABA: 226 alumnos (1º:102, 3º:69, 5º:55).
        47. PETO: 569 alumnos (1º:227, 3º:173, 5º:169).
        48. PROGRESO: 769 alumnos (1º:305, 3º:240, 5º:224).
        49. SAMAHIL: 154 alumnos (1º:62, 3º:43, 5º:49).
        50. SANTA ELENA: 151 alumnos (1º:55, 3º:53, 5º:43).
        51. SEYE: 329 alumnos (1º:126, 3º:110, 5º:93).
        52. SINANCHE: 111 alumnos (1º:42, 3º:38, 5º:31).
        53. SOTUTA: 248 alumnos (1º:101, 3º:74, 5º:73).
        54. SUCILA: 157 alumnos (1º:61, 3º:51, 5º:45).
        55. TAHDZIU: 169 alumnos (1º:73, 3º:52, 5º:44).
        56. TEABO: 248 alumnos (1º:97, 3º:75, 5º:76).
        57. TECAX: 394 alumnos (1º:163, 3º:123, 5º:108).
        58. TECOH: 330 alumnos (1º:141, 3º:105, 5º:84).
        59. TEKOM: 150 alumnos (1º:58, 3º:41, 5º:51).
        60. TELCHAC PUEBLO: 127 alumnos (1º:53, 3º:33, 5º:41).
        """
    },
    {
        "id": "mat_03",
        "metadata": { "sección": "Planteles 61-78 y Segundo Grupo", "tipo_documento": "Matrícula 2025-B" },
        "contenido": """
        DETALLE PLANTELES (ID 61-78):
        61. TEMAX: 233 alumnos (1º:85, 3º:77, 5º:71).
        62. TEPAKAM: 83 alumnos (1º:31, 3º:25, 5º:27).
        63. TICOPO: 213 alumnos (1º:87, 3º:68, 5º:58).
        64. TICUL: 800 alumnos (1º:308, 3º:249, 5º:243).
        65. TIMUCUY: 157 alumnos (1º:71, 3º:42, 5º:44).
        66. TIXMEHUAC: 162 alumnos (1º:54, 3º:58, 5º:50).
        67. TIZIMIN: 681 alumnos (1º:276, 3º:223, 5º:182).
        68. TUNKAS: 120 alumnos (1º:52, 3º:33, 5º:35).
        69. TZUCACAB: 391 alumnos (1º:158, 3º:120, 5º:113).
        70. UAYMA: 158 alumnos (1º:57, 3º:50, 5º:51).
        71. UCU: 157 alumnos (1º:58, 3º:58, 5º:41).
        72. UMAN: 741 alumnos (1º:298, 3º:221, 5º:222).
        73. VALLADOLID: 851 alumnos (1º:286, 3º:287, 5º:278).
        74. XOCCHEL: 193 alumnos (1º:74, 3º:61, 5º:58).
        75. X-MATKUIL: 1702 alumnos (1º:580, 3º:535, 5º:587).
        76. YAXCABÁ: 202 alumnos (1º:82, 3º:63, 5º:57).
        77. YAXKUKUL: 168 alumnos (1º:67, 3º:52, 5º:49).
        78. YOBAIN: 93 alumnos (1º:35, 3º:29, 5º:29).

        SEGUNDO GRUPO DE PLANTELES/CENTROS:
        1. BECAL: 143 alumnos (1º:66, 3º:41, 5º:36).
        2. CELESTUN: 126 alumnos (1º:49, 3º:44, 5º:33).
        3. CHIKINDZONOT: 150 alumnos (1º:63, 3º:45, 5º:42).
        4. DZITYA: 124 alumnos (1º:48, 3º:41, 5º:35).
        5. DZONOT CARRETERO: 85 alumnos (1º:29, 3º:24, 5º:32).
        6. KAUA: 166 alumnos (1º:69, 3º:51, 5º:46).
        7. PISTE: 253 alumnos (1º:85, 3º:80, 5º:88).
        8. POPOLNAH: 93 alumnos (1º:45, 3º:32, 5º:16).
        9. TIXCACALCUPUL: 176 alumnos (1º:63, 3º:58, 5º:55).
        10. TIXCANCAL: 125 alumnos (1º:44, 3º:35, 5º:46).
        11. XCAN: 203 alumnos (1º:75, 3º:67, 5º:61).
        """
    },

    # =========================================================================
    # BLOQUE 7: INFRAESTRUCTURA (Inventario de Salones y Turnos)
    # =========================================================================
    {
        "id": "infra_01",
        "metadata": { "sección": "Inventario de Salones y Turnos", "tipo_documento": "Infraestructura Educativa" },
        "contenido": """
        INVENTARIO DE SALONES Y DISTRIBUCIÓN DE TURNOS POR PLANTEL:

        1. Abalá: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        2. Acanceh: 12 Salones. 1º(Matutino-Discontinuo), 3º(Matutino-Discontinuo/Vespertino-Discontinuo), 5º(Vespertino-Discontinuo).
        3. Akil: 9 Salones. 1º(Matutino), 3º(Matutino/Vespertino), 5º(Vespertino).
        4. Baca: 12 Salones. 1º(Matutino), 3º(Matutino/Vespertino), 5º(Vespertino).
        5. Becanchen EMSAD: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        6. Buctzotz: 8 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        7. Cacalchén: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        8. Calotmul: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        9. Caucel: 15 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        10. Celestún EMSAD: 6 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        11. Cenotillo: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        12. Cepeda: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        13. Chacsinkin EMSAD: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        14. Chankom EMSAD: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        15. Chemax: 16 Salones. 1º(Matutino), 3º(Vespertino), 5º(Matutino/Vespertino).
        16. Chenkú: 28 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        17. Chichimilá: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        18. Chicxulub Pueblo: 9 Salones. 1º(Matutino/Vespertino), 3º(Matutino), 5º(Vespertino).
        19. Chikindzonot: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        20. Cholul: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        21. Colonia Yucatán: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        22. Cuzamá: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        23. Dzemul: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        24. Dzidzantún: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        25. Dzilam Gonzalez: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        26. Dzitás: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        27. Dzonot Carretero EMSAD: 6 Salones. 1º(Vespertino), 3º(Vespertino), 5º(Vespertino).
        28. Halachó: 12 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        29. Homún: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        30. Hunucmá: 15 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        31. Kanasín: 23 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        32. Kantunil: 4 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        33. Kaua EMSAD: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        34. Kimbilá: 9 Salones. 1º(Matutino), 3º(Matutino/Vespertino), 5º(Vespertino).
        35. Kinchil: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        36. Komchén: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        37. Muna: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        38. Opichén: 5 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        39. Peto: 18 Salones. 1º(Matutino), 3º(Matutino/Vespertino), 5º(Vespertino).
        40. Pisté EMSAD: 9 Salones. 1º(Vespertino), 3º(Matutino/Vespertino), 5º(Matutino).
        41. Popolnah EMSAD: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        42. Progreso: 30 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        43. Rio Lagartos: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        44. Sacalum: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        45. San José Tzal: 6 Salones. 1º(Mat-Disc/Vesp-Disc), 3º(Mat-Disc/Vesp-Disc), 5º(Mat-Disc/Vesp-Disc).
        46. Santa Elena: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        47. Santa Rosa: 45 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        48. Seyé: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        49. Sinanché: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        50. Sotuta: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        51. Sucilá: 4 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        52. Tahdziu EMSAD: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        53. Teabo: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        54. Tecax: 12 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        55. Tecoh: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        56. Tekit: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        57. Tekom: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        58. Telchac Pueblo: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        59. Temax: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        60. Temozón: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        61. Tepakam: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        62. Teya: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        63. Ticopó: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        64. Ticul: 18 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        65. Timucuy: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        66. Tinum: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        67. Tixcacalcupul EMSAD: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        68. Tixcancal EMSAD: 6 Salones. 1º(Vespertino), 3º(Matutino/Vespertino), 5º(Matutino).
        69. Tixkokob: 15 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        70. Tixméhuac: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        71. Tixpéual: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        72. Tizimín: 18 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        73. Tunkás: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        74. Tzucacab: 9 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        75. Uayma: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        76. Ucú: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        77. Umán: 18 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        78. Valladolid: 18 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        79. Xcan EMSAD: 6 Salones. 1º(Vespertino), 3º(Vespertino), 5º(Vespertino).
        80. X-Matkuil: 30 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        81. Xocchel: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        82. Xoclán: 30 Salones. 1º(Matutino/Vespertino), 3º(Matutino/Vespertino), 5º(Matutino/Vespertino).
        83. Yaxcabá: 6 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        84. Yaxkukul: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        85. Yobain: 3 Salones. 1º(Matutino), 3º(Matutino), 5º(Matutino).
        """
    },

    # =========================================================================
    # BLOQUE 8: PLAN ESTATAL DE DESARROLLO 2024-2030 (Directriz 3)
    # =========================================================================
    {
      "id": "chunk_01",
      "metadata": {
        "sección": "Visión General y Educación Humanista",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 85,
        "pagina_fin": 86
      },
      "contenido": "Yucatán vive el mejor momento de su historia con una educación humanista, una cultura viva que celebra sus raíces, y un pueblo que encuentra en la actividad física y deportiva una fuente de bienestar compartido. La Nueva Escuela Mexicana transforma conciencias y forma una ciudadanía con pensamiento crítico, con la fraternidad como valor esencial. Las juventudes de todos los rincones de nuestro estado, en igualdad de oportunidades, pueden acceder a una educación superior de excelencia. En Yucatán, la educación, cultura y deporte son los pilares de nuestra cohesión social. Directriz 3: Educación, Cultura y Deporte. 3.1. Educación humanista: Promueve un nuevo modelo educativo humanista, impulsando la 'Nueva Escuela Mexicana' (NEM) centrada en la 'revolución de conciencias', donde se fomente el pensamiento crítico, la empatía, la ética y la responsabilidad social. Esta vertiente busca transformar las aulas en espacios inclusivos y participativos, priorizando la capacitación docente, la actualización de los planes de estudio y el uso de tecnologías educativas. Incluye acciones para mejorar la infraestructura educativa y garantizar que todas las comunidades, incluidas las rurales e indígenas, tengan acceso equitativo a este modelo."
    },
    {
      "id": "chunk_02",
      "metadata": {
        "sección": "3.1 Educación Humanista - Rezago e Infraestructura",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 86,
        "pagina_fin": 87
      },
      "contenido": "Esta vertiente busca transformar las aulas en espacios inclusivos y participativos, priorizando la capacitación docente. 3.1.1. Objetivo estratégico: Reducir el rezago educativo en la educación básica y media superior en Yucatán. 3.1.1.1. Objetivo específico: Implementar procesos educativos innovadores. Líneas de Acción: Desarrollar actividades extracurriculares para estudiantes con rezago; establecer canales de comunicación con padres y maestros; implementar estrategias de apoyo emocional para evitar el abandono escolar; e impulsar la equidad de género y la interculturalidad. 3.1.1.2. Objetivo específico: Mejorar la infraestructura en las escuelas de comunidades maya hablantes con mayor rezago. Líneas de Acción: Renovar aulas para accesibilidad; optimizar infraestructura mediante internet y tecnologías; rehabilitar bibliotecas; verificar servicios básicos (agua, electricidad); fomentar participación comunitaria en mantenimiento; integrar equipos interdisciplinarios (psicología, trabajo social); e impulsar la modernización de instalaciones hidráulicas y eléctricas."
    },
    {
      "id": "chunk_03",
      "metadata": {
        "sección": "3.1 Educación Humanista - Analfabetismo y Cobertura",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 87,
        "pagina_fin": 87
      },
      "contenido": "Impulsar la modernización de instalaciones hidráulicas y eléctricas en escuelas. 3.1.1.3. Objetivo específico: Disminuir el analfabetismo prioritariamente en las comunidades maya hablantes. Líneas de Acción: Promover la lectura a lo largo de la vida; establecer círculos de lectura; fortalecer el hábito lector y pensamiento crítico mediante bibliotecas; diseñar actividades para población joven y adulta; fortalecer Misiones Culturales para disminuir el analfabetismo y formar a sus docentes bajo la Nueva Escuela Mexicana. 3.1.1.4. Objetivo específico: Ampliar la cobertura en educación básica y media superior, especialmente en áreas rurales. Líneas de Acción: Ejecutar acciones de infraestructura en comunidades maya-hablantes; estrategias para acceso y permanencia; fortalecer esquema de becas para estudiantes con dificultades económicas; e involucrar a líderes comunitarios para promover la inscripción escolar."
    },
    {
      "id": "chunk_04",
      "metadata": {
        "sección": "3.1 Educación Humanista - Currículo NEM y Docentes",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 88,
        "pagina_fin": 88
      },
      "contenido": "Involucrar a líderes comunitarios para promover la inscripción escolar. 3.1.1.5. Objetivo específico: Implementar currículos educativos, incorporando enfoques pedagógicos de la Nueva Escuela Mexicana (NEM). Líneas de Acción: Formación y actualización docente en la NEM; implementar planes de estudio acordes a la NEM; valorar procesos de aprendizaje para evaluación formativa; fomentar pensamiento crítico, científico, ético y emocional; fomentar inclusión de necesidades educativas específicas; y desarrollar proyectos comunitarios transversales. 3.1.1.6. Objetivo específico: Mejorar las condiciones laborales de los trabajadores de la educación. Líneas de Acción: Fomentar comunidades profesionales de aprendizaje; mejorar sistema de reconocimiento profesional; garantizar derechos laborales y humanos; asegurar ambiente laboral saludable (físico y emocional); prevenir demandas injustificadas; y gestionar salario justo valorando formación y experiencia."
    },
    {
      "id": "chunk_05",
      "metadata": {
        "sección": "3.1 Educación Intercultural y Lengua Maya",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 88,
        "pagina_fin": 89
      },
      "contenido": "Gestionar salario justo para docentes. 3.1.2. Objetivo estratégico: Garantizar una educación intercultural bilingüe en las comunidades maya hablantes. 3.1.2.1. Objetivo específico: Potenciar el reconocimiento de la lengua materna con énfasis en la lengua maya. Líneas de Acción: Generar espacios educativos para ambas lenguas; fortalecer diálogos interculturales; fomentar respeto y tolerancia; fortalecer identidad maya mediante enseñanza de la lengua en todos los niveles y espacios públicos/privados; incentivar conocimiento de historia y cosmovisión yucateca; diseñar estrategias para educandos con enfoque intercultural. 3.1.2.2. Objetivo específico: Reconocer a comunidades afrodescendientes y migrantes. Líneas de Acción: Proyectos de intercambio escuela-comunidad; fomentar empatía hacia diferencias culturales; proyectos que visibilicen raíces culturales; y talleres sobre diversidad y no discriminación."
    },
    {
      "id": "chunk_06",
      "metadata": {
        "sección": "3.1 Educación Indígena - Infraestructura y Formación",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 89,
        "pagina_fin": 90
      },
      "contenido": "Talleres sobre diversidad y no discriminación. 3.1.2.3. Objetivo específico: Mejorar infraestructura escolar en comunidades maya-hablantes. Líneas de Acción: Espacios de calidad con servicios básicos; valorar aumento de docentes según necesidades; elaborar material académico pertinente a la Nueva Educación Indígena; promover conectividad y TIC. 3.1.2.4. Objetivo específico: Capacitación docente en lengua maya. Líneas de Acción: Coordinar formación docente en Nueva Educación Indígena; diseñar perfil pertinente para docentes; promover aprendizaje de maya en escuelas para identidad cultural; certificación de maestros en lengua maya. 3.1.2.5. Objetivo específico: Asegurar educación integral y humanista en lengua maya. Líneas de Acción: Formación docente en filosofía maya y equidad; adecuaciones curriculares lingüísticas; fortalecer valores de interculturalidad; integrar lengua maya como asignatura."
    },
    {
      "id": "chunk_07",
      "metadata": {
        "sección": "3.1 Educación Básica y Media - Tecnología e Inclusión",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 90,
        "pagina_fin": 91
      },
      "contenido": "Integrar lengua maya como asignatura. 3.1.3. Objetivo estratégico: Extender la Nueva Escuela Mexicana en educación básica y media superior. 3.1.3.1. Objetivo específico: Fortalecer infraestructura con tecnología. Líneas de Acción: Incrementar equipamiento informático y conectividad; fortalecer enseñanza con TIC en media superior; formación docente en uso didáctico de tecnología; mantenimiento de edificios. 3.1.3.2. Objetivo específico: Diseñar acciones para la NEM. Líneas de Acción: Talleres tecnológicos para docentes; fortalecer educación humanista; coordinación interinstitucional; actualizar materiales educativos alineados a la NEM. 3.1.3.3. Objetivo específico: Garantizar educación especial inclusiva. Líneas de Acción: Personal para USAER; creación de nuevos Centros de Atención Múltiple (CAM); convenios de apoyo; formación docente para atender diversas capacidades; estrategias colaborativas entre especialistas y padres."
    },
    {
      "id": "chunk_08",
      "metadata": {
        "sección": "3.1 Educación Media Superior - Pertinencia y Evaluación",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 91,
        "pagina_fin": 92
      },
      "contenido": "Estrategias colaborativas entre especialistas y padres. 3.1.3.4. Objetivo específico: Mejorar eficacia en educación media superior. Líneas de Acción: Vincular educación con sector productivo; fomentar comunicación con padres; talleres sobre violencia escolar; consolidar educación dual; acciones innovadoras ante necesidades actuales; garantizar acceso inclusivo. 3.1.3.5. Objetivo específico: Mejorar pertinencia de planes de estudio. Líneas de Acción: Formación docente en metodologías NEM; implementación de evaluación formativa; uso de herramientas tecnológicas; trabajo colaborativo estudiantil; mejorar instrumentos de evaluación. 3.1.3.6. Objetivo específico: Mejorar evaluación educativa. Líneas de Acción: Fomentar evaluación entre pares docentes; autoevaluación docente; verificar aplicación de planeación educativa; identificar áreas de mejora mediante evaluación periódica de métodos de enseñanza."
    },
    {
      "id": "chunk_09",
      "metadata": {
        "sección": "3.2 Cultura con Identidad - Infraestructura",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 92,
        "pagina_fin": 93
      },
      "contenido": "3.2. Cultura con identidad: Rescata, preserva y promueve tradiciones y expresiones artísticas, fomentando la participación comunitaria y democratización cultural. 3.2.1. Objetivo estratégico: Mejorar infraestructura de espacios culturales en municipios. 3.2.1.1. Objetivo específico: Incrementar infraestructura cultural integral. Líneas de Acción: Coordinar oferta con casas de cultura y gremios; modernizar espacios existentes; fomentar aprecio por patrimonio; diagnóstico de infraestructura. 3.2.1.2. Objetivo específico: Colaboración para creación de casas de cultura. Líneas de Acción: Crear modelo adaptable de casa de cultura; diagnóstico de necesidades municipales; concientizar sobre beneficios de espacios culturales; red de municipios para gestión cultural. 3.2.1.3. Objetivo específico: Integración municipal a programación estatal. Líneas de Acción: Presencia de creadores yucatecos en municipios; programación en escuelas públicas; agenda cultural conjunta estado-municipios."
    },
    {
      "id": "chunk_10",
      "metadata": {
        "sección": "3.2 Cultura - Consejos Regionales y Patrimonio",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 93,
        "pagina_fin": 94
      },
      "contenido": "Agenda cultural conjunta estado-municipios. 3.2.1.4. Objetivo específico: Integración de consejos consultivos de arte y cultura regionales. Líneas de Acción: Gestionar creación de consejos; asesorar en diseño de programación; talleres de gestión cultural para integrantes; involucrar a la comunidad en decisiones. 3.2.1.5. Objetivo específico: Actualizar estadística de infraestructura cultural. Líneas de Acción: Directorio de museos y bibliotecas; colaboración con universidades; plataforma digital de datos culturales; visitas de verificación; plataforma de promoción de actividades. 3.2.2. Objetivo estratégico: Ampliar infraestructura y patrimonio cultural. 3.2.2.1. Objetivo específico: Preservación del patrimonio. Líneas de Acción: Estrategias acordes a cosmovisión maya; apropiación social del patrimonio; inclusión en planes de desarrollo urbano y turístico; archivos locales comunitarios."
    },
    {
      "id": "chunk_11",
      "metadata": {
        "sección": "3.2 Cultura - Catálogos, Festivales y Difusión",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 94,
        "pagina_fin": 95
      },
      "contenido": "Archivos locales comunitarios. 3.2.2.2. Objetivo específico: Elaborar catálogo del patrimonio cultural. Líneas de Acción: Catálogos literarios municipales; fondo de consulta Rita Cetina Gutiérrez; actualizar catálogos patrimoniales; colaboración interinstitucional. 3.2.2.3. Objetivo específico: Difundir patrimonio a través de festivales. Líneas de Acción: Calendario de festividades coordinado; talleres gastronómicos; promover creación musical como patrimonio; profesionalizar gremio audiovisual; establecer al Estado como destino fílmico. 3.2.2.4. Objetivo específico: Preservar y difundir grandeza patrimonial en casas de cultura. Líneas de Acción: Estudios y publicaciones locales; charlas y conferencias coordinadas; capacitaciones para profesionalización cultural; identificar expresiones en riesgo de desaparecer."
    },
    {
      "id": "chunk_12",
      "metadata": {
        "sección": "3.2 Cultura - Artistas y Creadores",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 96,
        "pagina_fin": 97
      },
      "contenido": "Identificar expresiones en riesgo de desaparecer. 3.2.3. Objetivo estratégico: Aumentar obras e iniciativas de creadores. 3.2.3.1. Objetivo específico: Actualizar censo de agentes culturales. Líneas de Acción: Actualizar información con municipios; registro estatal por categoría; protocolo estandarizado de registro; plataforma de autogestión de datos. 3.2.3.2. Objetivo específico: Reconocer a artistas con labor social. Líneas de Acción: Difusión de eventos de reconocimiento; visibilizar trabajo social artístico; establecer categorías de reconocimiento; documentar trayectorias. 3.2.3.3. Objetivo específico: Incentivar comercialización de bienes artísticos. Líneas de Acción: Eventos y exposiciones para mercado local; convenios laborales con empresas; presencia en ferias fuera del estado."
    },
    {
      "id": "chunk_13",
      "metadata": {
        "sección": "3.2 Cultura - Profesionalización y Artistas Mayas",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 97,
        "pagina_fin": 97
      },
      "contenido": "Presencia en ferias fuera del estado. 3.2.3.4. Objetivo específico: Impulsar profesionalización artística. Líneas de Acción: Canalizar artistas a recursos públicos; programas de mentoría; apoyo para convocatorias y concursos nacionales/internacionales. 3.2.3.5. Objetivo específico: Impulsar artistas mayas. Líneas de Acción: Inclusión en ferias y festivales; rutas turísticas a talleres mayas; focalizar promoción en comunidades de artistas; eventos inmersivos en lengua maya. 3.2.3.6. Objetivo específico: Promover música yucateca. Líneas de Acción: Difusión para ampliar audiencias; inclusión en eventos estatales; rutas turísticas musicales."
    },
    {
      "id": "chunk_14",
      "metadata": {
        "sección": "3.3 Cultura Física y Deporte - Espacios y Salud",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 98,
        "pagina_fin": 98
      },
      "contenido": "3.3. Cultura física y deporte: Fomenta la cultura física para mejorar la salud y el tejido social, mediante espacios deportivos, formación de atletas y actividades recreativas inclusivas. 3.3.1. Objetivo estratégico: Extender la cultura física. 3.3.1.1. Objetivo específico: Optimizar espacios de recreación para enfrentar obesidad. Líneas de Acción: Dotar infraestructura en parques y escuelas; fomentar uso de espacios municipales; rehabilitar y modernizar espacios recreativos. 3.3.1.2. Objetivo específico: Coordinación salud-cultura física contra sedentarismo. Líneas de Acción: Impulsar deporte en esquemas de salud; ampliar cobertura de deporte social; campañas conjuntas sobre actividad física. 3.3.1.3. Objetivo específico: Estilo de vida saludable en niños y adolescentes. Líneas de Acción: Coordinación salud-educación-deporte en escuelas; talleres de alimentación e higiene; eventos deportivos infantiles."
    },
    {
      "id": "chunk_15",
      "metadata": {
        "sección": "3.3 Deporte - Sectores Vulnerables y Ligas",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 98,
        "pagina_fin": 99
      },
      "contenido": "Eventos deportivos infantiles. 3.3.1.4. Objetivo específico: Acceso al deporte para sectores vulnerables. Líneas de Acción: Talleres de recreación y salud; mejorar instalaciones municipales; identificar necesidades específicas de población vulnerable. 3.3.1.5. Objetivo específico: Descentralización regional del deporte. Líneas de Acción: Acuerdos estatales-municipales; Centros de Promoción y Desarrollo Deportivo en el interior; garantizar accesibilidad. 3.3.2. Objetivo estratégico: Impulsar la práctica del deporte. 3.3.2.1. Objetivo específico: Vinculación municipal para deporte social y juegos tradicionales. Líneas de Acción: Fomentar deporte social y juegos tradicionales en municipios; redes de colaboración intermunicipal. 3.3.2.2. Objetivo específico: Mejorar centros deportivos municipales. Líneas de Acción: Mantenimiento preventivo; ligas infantiles y amateur intermunicipales; equipamiento de calidad."
    },
    {
      "id": "chunk_16",
      "metadata": {
        "sección": "3.3 Deporte Escolar y Alto Rendimiento",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 99,
        "pagina_fin": 100
      },
      "contenido": "Equipamiento de calidad. 3.3.2.3. Objetivo específico: Fortalecer educación física escolar. Líneas de Acción: Monitorear ligas escolares; uso de parques para activación física; actualizar currículo de educación física (inclusivo). 3.3.2.4. Objetivo específico: Fortalecer centros de desarrollo y ligas estatales. Líneas de Acción: Promover deporte amateur; ligas intermunicipales; rehabilitar centros deportivos. 3.3.3. Objetivo estratégico: Ampliar deporte de alto rendimiento. 3.3.3.1. Objetivo específico: Identificar talentos deportivos. Líneas de Acción: Coordinación con Instituto del Deporte y escuelas para detección; fortalecer academias para representar a Yucatán; jornadas de talentos. 3.3.3.2. Objetivo específico: Potenciar deportistas de alto rendimiento. Líneas de Acción: Planes de entrenamiento coordinados; capacitación de entrenadores; programas integrales (físico, técnico, psicológico)."
    },
    {
      "id": "chunk_17",
      "metadata": {
        "sección": "3.3 Deporte - Paralímpicos, Medicina y CONADE",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 100,
        "pagina_fin": 101
      },
      "contenido": "Programas integrales para deportistas. 3.3.3.3. Objetivo específico: Potenciar deportistas paralímpicos. Líneas de Acción: Entrenamientos para nivel nacional; detección de prospectos con discapacidad; certificación de entrenadores paralímpicos. 3.3.3.4. Objetivo específico: Medicina del deporte y ciencias aplicadas. Líneas de Acción: Modelos efectivos de salud física/mental; revisiones médicas periódicas; prevención de lesiones. 3.3.3.5. Objetivo específico: Mejorar infraestructura para alto rendimiento. Líneas de Acción: Facilitar espacios estatales a deportistas; gestionar uso de clubes; cumplir estándares de seguridad y accesibilidad. 3.3.3.6. Objetivo específico: Vincular con CONADE e institutos. Líneas de Acción: Fomentar mejores prácticas nacionales; fortalecer selecciones estatales; acuerdos con CONADE para cursos."
    },
    {
      "id": "chunk_18",
      "metadata": {
        "sección": "3.4 Educación Superior - Acceso e Inclusión",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 102,
        "pagina_fin": 103
      },
      "contenido": "3.4. Educación superior, inclusiva, equitativa y de excelencia: Garantiza acceso de calidad con atención a comunidades marginadas, promoviendo vinculación productiva y perspectiva de género. 3.4.1. Objetivo estratégico: Incrementar accesibilidad inclusiva. 3.4.1.1. Objetivo específico: Expandir acceso y equidad. Líneas de Acción: Educación superior virtual en áreas rurales; tutoría para bajo nivel académico; becas para comunidades indígenas y rurales; asesorías de pares; flexibilidad de horarios y educación a distancia. 3.4.1.2. Objetivo específico: Igualdad de género y diversidad. Líneas de Acción: Espacios para participación femenina en STEM; ambiente inclusivo y cero discriminación; talleres de sensibilización; espacios seguros. 3.4.1.3. Objetivo específico: Combatir el acoso. Líneas de Acción: Capacitación en prevención; protocolos de actuación claros; sensibilización sobre denuncia."
    },
    {
      "id": "chunk_19",
      "metadata": {
        "sección": "3.4 Educación Superior - Salud Mental y Entorno",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 103,
        "pagina_fin": 103
      },
      "contenido": "Sensibilización sobre denuncia de acoso. 3.4.1.4. Objetivo específico: Salud mental y bienestar. Líneas de Acción: Talleres manejo de estrés; campañas de salud mental y apoyo mutuo; gestión con CISAME; actividades recreativas para equilibrio vida-estudio. 3.4.1.5. Objetivo específico: Generar entorno inclusivo y equitativo. Líneas de Acción: Cuotas preferenciales para entornos desfavorecidos; transporte para estudiantes de municipios sin servicios educativos; difusión en comunidades marginadas; políticas de permanencia escolar. 3.4.2. Objetivo estratégico: Expandir acceso pertinente y de excelencia. 3.4.2.1. Objetivo específico: Planes de estudio pertinentes. Líneas de Acción: Actualización docente en nuevas tecnologías; vinculación media superior-superior; habilidades emergentes (IA, sustentabilidad); colaboración con industrias; convenios empresariales para prácticas."
    },
    {
      "id": "chunk_20",
      "metadata": {
        "sección": "3.4 Educación Superior - Humanismo y Excelencia",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 104,
        "pagina_fin": 105
      },
      "contenido": "Convenios empresariales para prácticas. 3.4.2.2. Objetivo específico: Integrar humanismo mexicano. Líneas de Acción: Formación integral y ética comunitaria; habilidades gerenciales y liderazgo ético; congresos sobre ética profesional; proyectos de responsabilidad social; pensamiento crítico. 3.4.2.3. Objetivo específico: Evaluación continua. Líneas de Acción: Retroalimentación oportuna; modificar actividades según evaluación; atención a rezago; feedback específico. 3.4.2.4. Objetivo específico: Evaluar excelencia académica. Líneas de Acción: Vínculos con acreditadoras; evaluar docencia, investigación y gestión; incentivos a investigación; autoevaluación interna; congresos internacionales."
    },
    {
      "id": "chunk_21",
      "metadata": {
        "sección": "3.4 Educación Superior - Infraestructura y Movilidad",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 105,
        "pagina_fin": 106
      },
      "contenido": "Congresos internacionales. 3.4.2.5. Objetivo específico: Mejorar infraestructura y recursos. Líneas de Acción: Apoyos para equipo electrónico y acceso (rampas); colaboración para gestión de recursos; alianzas para internet; modernización de seguridad y tecnología; recursos digitales y bibliotecas; espacios de innovación (Makerspaces); espacios de tutoría. 3.4.2.6. Objetivo específico: Intercambio y movilidad internacional. Líneas de Acción: Convenios para becas de movilidad; difusión accesible de intercambios; ferias internacionales; doble titulación; fortalecimiento del idioma inglés en el extranjero. 3.4.3. Objetivo estratégico: Promover innovación, investigación y desarrollo sostenible."
    },
    {
      "id": "chunk_22",
      "metadata": {
        "sección": "3.4 Educación Superior - Tecnología e Investigación",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 106,
        "pagina_fin": 107
      },
      "contenido": "3.4.3. Objetivo estratégico: Promover innovación e investigación. 3.4.3.1. Objetivo específico: Competencias digitales. Líneas de Acción: Capacitación en tecnologías emergentes (IA, robótica); laboratorios de innovación; centros de tecnología; becas empresariales para cursos tech; alianzas con empresas de vanguardia. 3.4.3.2. Objetivo específico: Fortalecer investigación. Líneas de Acción: Transferencia de tecnología vinculada a industria local; investigación en comunidades marginadas; fondos para salud y ciencias sociales; centros de excelencia en turismo sostenible y agrotecnología; difusión de impacto de investigación."
    },
    {
      "id": "chunk_23",
      "metadata": {
        "sección": "3.4 Educación Superior - Comunidad y Sostenibilidad",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 107,
        "pagina_fin": 107
      },
      "contenido": "Difusión de impacto de investigación. 3.4.3.3. Objetivo específico: Conexión con comunidad y responsabilidad social. Líneas de Acción: Comunidades de diálogo estudiantil; inserción técnica en empresas; servicio comunitario curricular; alianzas con ONGs para impacto social; voluntariado; proyectos de desarrollo comunitario sostenible. 3.4.3.4. Objetivo específico: Conciencia ambiental y sostenibilidad. Líneas de Acción: Ajustar planes educativos a conservación; campañas de reforestación/limpieza; reciclaje y energías renovables en campus; alianzas de conservación; jardines o laboratorios de biodiversidad. 3.4.3.5. Objetivo específico: Innovación y cultura emprendedora. Líneas de Acción: Proyectos de autoempleo; talleres de emprendimiento; vínculos para inserción laboral; cursos online de innovación."
    },
    {
      "id": "chunk_24",
      "metadata": {
        "sección": "3.5 Empoderamiento de la Mujer - Acceso y Becas",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 108,
        "pagina_fin": 109
      },
      "contenido": "3.5. Empoderamiento educativo y deportivo para las mujeres: Promueve acceso a programas que fortalezcan desarrollo integral, eliminando barreras y creando espacios seguros. 3.5.1. Objetivo estratégico: Aumentar acceso de mujeres a modelos educativos y deportivos. 3.5.1.1. Objetivo específico: Expandir acceso en sectores vulnerables. Líneas de Acción: Plataformas virtuales; centros deportivos con perspectiva de género; ligas femeninas inclusivas. 3.5.1.2. Objetivo específico: Disminuir brechas de desigualdad. Líneas de Acción: Campañas en comunidades con rezago; espacios de liderazgo; programas adaptados a zonas rurales e indígenas. 3.5.1.3. Objetivo específico: Difusión de modelos. Líneas de Acción: Ferias educativas y deportivas municipales; lenguaje inclusivo. 3.5.1.4. Objetivo específico: Acceso a becas. Líneas de Acción: Difusión de sistemas de becas; alianzas para identificar oportunidades; priorizar grupos vulnerables. 3.5.1.5. TIC: Portal de ofertas educativas/deportivas; plataformas en línea."
    },
    {
      "id": "chunk_25",
      "metadata": {
        "sección": "3.5 Empoderamiento de la Mujer - Liderazgo",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 109,
        "pagina_fin": 110
      },
      "contenido": "Plataformas en línea. 3.5.2. Objetivo estratégico: Incorporar modelos de liderazgo y empoderamiento. 3.5.2.1. Objetivo específico: Procesos de formación en liderazgo. Líneas de Acción: Eventos con mujeres líderes; capacitación para liderazgo educativo/deportivo; programas de mentoría. 3.5.2.2. Objetivo específico: Habilidades de liderazgo. Líneas de Acción: Capacitación en confianza y comunicación; equidad de género y derechos humanos; talleres de toma de decisiones. 3.5.2.3. Objetivo específico: Transformación profesional. Líneas de Acción: Evaluar necesidades profesionales; mentoría de líderes diversos sectores; acceso a financiamiento para emprendimiento. 3.5.2.4. Objetivo específico: Mujer como promotora. Líneas de Acción: Impulsar promotoras locales; inclusión en comités y consejos; roles de liderazgo en equipos."
    },
    {
      "id": "chunk_26",
      "metadata": {
        "sección": "3.5 Empoderamiento de la Mujer - Espacios Seguros",
        "tipo_documento": "Plan Estatal de Desarrollo 2024-2030",
        "pagina_inicio": 110,
        "pagina_fin": 112
      },
      "contenido": "Roles de liderazgo en equipos. 3.5.2.5. Objetivo específico: Identificar líderes con responsabilidad social. Líneas de Acción: Diagnósticos comunitarios; difundir historias de éxito. 3.5.2.6. Premio de liderazgo: Coordinar premio; convocatorias para nominación comunitaria. 3.5.3. Objetivo estratégico: Fortalecer espacios seguros e inclusivos. 3.5.3.1. Objetivo específico: Áreas seguras en recreación. Líneas de Acción: Adaptar infraestructura; participación femenina en diseño; áreas exclusivas. 3.5.3.2. Objetivo específico: Perspectiva de género e inclusión. Líneas de Acción: Gestionar recursos para bienestar; mantenimiento óptimo; programas desde diseño hasta implementación. 3.5.3.5. Objetivo específico: Construir espacios dirigidos a mujeres. Líneas de Acción: Infraestructura con seguridad (iluminación, vigilancia); protocolos contra acoso. 3.5.3.6. Tecnología: Espacios con tecnología de vanguardia y servicios complementarios (guarderías)."
    },

    # =========================================================================
    # BLOQUE 9: INFORMES PRINCIPALES (Nuevo Bloque)
    # =========================================================================
    {
        "id": "inf_01",
        "metadata": { "sección": "Resumen Ejecutivo", "tipo_documento": "Informe Principal" },
        "contenido": "[ESPACIO RESERVADO PARA EL CONTENIDO DE LOS INFORMES PRINCIPALES. POR FAVOR, PEGUE AQUÍ EL TEXTO DEL INFORME CUANDO ESTÉ DISPONIBLE.]"
    }
]

# ---------------------------------------------------------
# 2. CONFIGURACIÓN DEL SISTEMA
# ---------------------------------------------------------
def generar_contexto_sistema(datos):
    contexto = "ERES ALTIUS COBAY, UN SISTEMA DE CONSULTORÍA INTELIGENTE PARA EL COLEGIO DE BACHILLERES DEL ESTADO DE YUCATÁN.\n"
    contexto += "Tu misión es fortalecer el ecosistema educativo proporcionando respuestas precisas basadas en la siguiente documentación oficial:\n\n"
    contexto += "1. REGLAMENTO INTERIOR DE TRABAJO (RIT): Obligaciones, disciplina y condiciones laborales.\n"
    contexto += "2. REGLAMENTO ACADÉMICO: Trámites, derechos y obligaciones de alumnos.\n"
    contexto += "3. CONTRATO COLECTIVO DE TRABAJO (CCT): Derechos sindicales y prestaciones.\n"
    contexto += "4. DIRECTORIO INSTITUCIONAL: Cargos, teléfonos y organigrama.\n"
    contexto += "5. PLANTELES Y MATRÍCULA: Estadísticas de alumnos por plantel y semestre.\n"
    contexto += "6. INFRAESTRUCTURA: Inventario de salones y distribución de turnos por semestre.\n"
    contexto += "7. PLAN ESTATAL DE DESARROLLO 2024-2030 (Directriz 3): Educación, Cultura y Deporte, Nueva Escuela Mexicana.\n"
    contexto += "8. INFORMES PRINCIPALES: Documentación estratégica y reportes de gestión.\n\n"
    contexto += "BASE DE CONOCIMIENTO UNIFICADA:\n"
    
    for item in datos:
        tipo_doc = item['metadata'].get('tipo_documento', 'Documento General')
        seccion = item['metadata']['sección']
        contenido = item['contenido']
        
        contexto += f"--- [{tipo_doc}] SECCIÓN: {seccion} ---\n"
        contexto += f"{contenido}\n\n"
    
    contexto += "\nINSTRUCCIONES PARA RESPONDER:\n"
    contexto += "1. IDENTIDAD: Preséntate como 'ALTIUS COBAY' si te preguntan quién eres.\n"
    contexto += "2. CLASIFICACIÓN: Identifica si la consulta es Laboral, Académica, Administrativa, Estadística o de Infraestructura.\n"
    contexto += "3. PRECISIÓN: Usa datos exactos del bloque de Matrícula o Infraestructura cuando se requieran cifras o fechas.\n"
    contexto += "4. CITA: Menciona siempre la fuente (ej. 'Según el Inventario de Infraestructura...' o 'Con base en el Reglamento Académico...').\n"
    contexto += "5. BREVEDAD: Tus respuestas deben ser directas y concisas. No excedas las 150 palabras a menos que sea estrictamente necesario. Prioriza listas y datos duros. Optimiza tu respuesta para que quepa en menos de 200 palabras.\n"
    return contexto

# Generar el prompt del sistema (Asegúrese de que DATOS_RAG tenga el contenido real)
SYSTEM_PROMPT = generar_contexto_sistema(DATOS_RAG)

# ---------------------------------------------------------
# 3. INTERFAZ DE STREAMLIT Y CLIENTE OPENROUTER
# ---------------------------------------------------------
st.set_page_config(page_title="ALTIUS COBAY - Consultoría", page_icon="🎓", layout="wide")

# === INICIO DEL BLOQUE DE LOGO ===
# Verificamos si el archivo existe para evitar errores si no se ha subido
if os.path.exists("logo.png"):
    # Creamos 3 columnas para centrar la imagen (la columna del medio es más ancha)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", width=200) # Ajuste el 'width' (ancho) según necesite
# === FIN DEL BLOQUE DE LOGO ===

st.title("🎓 ALTIUS COBAY")
st.subheader("Consultoría Inteligente")
st.markdown("**Fortaleciendo el ecosistema educativo del COBAY con Mistral Small**")
st.markdown("---")

# --- CONFIGURACIÓN SEGURA DE API KEY ---
BASE_URL = "https://openrouter.ai/api/v1"

# === MODELO DE MISTRAL ===
MODEL_NAME = "mistralai/mistral-small-creative"

# Recuperación segura de la clave desde st.secrets
api_key = None
try:
    api_key = st.secrets["OPENROUTER_API_KEY"]
except (FileNotFoundError, KeyError):
    pass

# Inicialización del cliente
client = None
if api_key:
    try:
        client = OpenAI(
            base_url=BASE_URL,
            api_key=api_key
        )
    except Exception as e:
        st.error(f"Error al iniciar el cliente: {e}")
else:
    st.warning("⚠️ La API Key no está configurada. Por favor, añada 'OPENROUTER_API_KEY' en los 'Secrets' de Streamlit Cloud.")
    st.stop()

# --- HISTORIAL Y CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Consulta a ALTIUS (Ej: ¿Cuántos salones tiene el plantel Acanceh? o ¿Cuándo inician clases?)"):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Construcción de mensajes
            messages_api = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in st.session_state.messages:
                messages_api.append({"role": msg["role"], "content": msg["content"]})

            # Llamada al modelo con LÍMITE DE TOKENS (Cost control)
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages_api,
                stream=True,
                temperature=0.3,
                max_tokens=300  # <--- Límite duro para controlar costos
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error técnico en el sistema ALTIUS: {e}")
