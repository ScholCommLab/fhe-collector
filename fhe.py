from app import create_app
from app import import_from_api
import click


app = create_app()
app.app_context().push()

# TODO: show progress of api requests in shell
@app.cli.command()
def setup_db():
    import_from_csv()
    create_doi_urls()
    create_ncbi_urls()
    create_unpaywall_urls()


@app.cli.command()
def delete_db():
    delete_dois()
    delete_urls()
    delete_fbrequests()


@app.cli.command()
def reset_db():
    delete_db()
    setup_db()


@app.cli.command()
def import_from_csv():
    from app import import_from_csv
    import_from_csv(app.config['CSV_FILENAME'])


@app.cli.command()
def create_doi_urls():
    from app import create_doi_urls
    create_doi_urls()


@app.cli.command()
def create_ncbi_urls():
    from app import create_ncbi_urls
    create_ncbi_urls()


@app.cli.command()
def create_unpaywall_urls():
    from app import create_unpaywall_urls
    create_unpaywall_urls()


@app.cli.command()
def delete_dois():
    from app import delete_dois
    delete_dois()


@app.cli.command()
def delete_urls():
    from app import delete_urls
    delete_urls()


@app.cli.command()
def delete_fbrequests():
    from app import delete_fbrequests
    delete_fbrequests()


@app.cli.command()
def export_data():
    from app import export_data
    export_data()


from json import dumps, loads
from flask import request, jsonify

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/api')
@app.route('/api/v1')
def api():
    return "API Homepage"


@app.route('/api/v1/add_data', methods=['POST'])
def add_data():
    response_status = 'error'
    try:
        if request.headers['Content-Type'] == 'application/json':
            data = request.json
            if isinstance(data, list):
                is_data_valid = True
                for entry in data:
                    if 'doi' in entry and 'url' in entry:
                        if not isinstance(entry['doi'], str) and not isinstance(entry['url'], string):
                            is_data_valid = False
                    else:
                        is_data_valid = False
                        response = '"doi" or "url" key missing in JSON entry {}.'.format(entry)
                if is_data_valid:
                    resp_func = import_from_api(data)
                    if resp_func:
                        response = resp_func
                        response_status = 'ok'
                    else:
                        response = 'Error: JSON from API could not be stored in database.'
            else:
                response = 'No list of data in JSON.'
        else:
            response = 'No JSON delivered.'
    except:
        response = 'Undefined error.'

    return jsonify({"status": response_status, 'content': response})
