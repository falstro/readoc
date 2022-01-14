from .embed import filename, pipe, accept

import os


def _plantuml(fmt, headers, body):
    fname = filename('plantuml', fmt, body)
    JAVA_HOME = os.getenv('JAVA_HOME')
    if JAVA_HOME:
        JAVA = JAVA_HOME + '/bin/java'
    else:
        JAVA = '/usr/bin/java'

    cmd = [JAVA]

    JAR = os.getenv('PLANTUML_JAR', '/usr/share/plantuml/plantuml.jar')
    PATH = os.getenv('PLANTUML_PATH')
    RELATIVE_INCLUDE = os.getenv('RELATIVE_INCLUDE')

    if PATH:
        cmd.append('-Dplantuml.include.path=' + PATH)
    if RELATIVE_INCLUDE:
        cmd.append('-DRELATIVE_INCLUDE=' + RELATIVE_INCLUDE)

    cmd.extend(['-jar', JAR, '-T' + fmt, '-p'])
    pipe(cmd, fname, body)
    return fmt, fname


def plantuml(fmts, headers, body):
    # fmt = accept(fmts, 'eps', 'pdf', 'vdx', 'svg', 'png')
    return _plantuml(accept(fmts, 'eps', 'vdx', 'svg', 'png'), headers, body)


def plantuml_png(fmts, headers, body):
    # fmt = accept(fmts, 'eps', 'pdf', 'vdx', 'svg', 'png')
    return _plantuml(accept(fmts, 'png'), headers, body)


EMBED = {
    'plantuml': plantuml,
    'puml': plantuml,
    'puml-png': plantuml_png,
}
