#! /usr/bin/env python
"""
    WSGI APP to convert multiple pdf files into one pdf using ghostcript As a webservice

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import json
import tempfile

from werkzeug.wsgi import wrap_file
from werkzeug.wrappers import Request, Response
from executor import execute


@Request.application
def application(request):
    """
    To use this application, the user must send a POST request with
    base64 or form encoded encoded PDF files content and the ghostcript Options in
    request data, with keys 'base64_html' and 'options'.
    The application will return a response with the PDF file.
    """
    if request.method != 'POST':
        return

    request_is_json = request.content_type.endswith('json')

    with tempfile.NamedTemporaryFile(suffix='.pdf') as source_file:

        if request_is_json:
            # If a JSON payload is there, all data is in the payload
            payload = json.loads(request.data)
            source_file.write(payload['contents'].decode('base64'))
            options = payload.get('options', {})
        elif request.files:
            # First check if any files were uploaded
            source_file.write(request.files['file0'].read())
            # Load any options that may have been provided in options
            options = json.loads(request.form.get('options', '{}'))

        source_file.flush()

        # Evaluate argument to run with subprocess
        #ghostscript -q -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dUseCIEColor -sOutputFile=$outputName -dBATCH $files";

        args = ['ghostscript']
        args.append('-q -sDEVICE=pdfwrite -dCompatibilityLevel=1.4')
        args.append('-dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dUseCIEColor')
        
        # Add Global Options
        if options:
            for option, value in options.items():
                args.append('-d%s' % option)
                if value:
                    args.append('="%s"' % value)

        # Add source file name and output file name
        file_name = source_file.name
        args += ["-sOutputFile=" + file_name +".pdf", "-dBATCH " + file_name]

        # Execute the command using executor
        execute(' '.join(args))

        return Response(
            wrap_file(request.environ, open(file_name + '.pdf')),
            mimetype='application/pdf',
        )


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple(
        '127.0.0.1', 5000, application, use_debugger=True, use_reloader=True
    )
