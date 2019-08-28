import click
from flask import jsonify
from flask import render_template
from flask import request
from app import create_app
from app import import_dois_from_api


app = create_app()
app.app_context().push()


@app.cli.command()
@click.argument('filename', type=click.Path(exists=True), required=False)
def init_data(filename=None):
    """Import raw data from csv file.

    The filepath can be manually passed with the argument `filename`.

    Parameters
    ----------
    filename : string
        Filepath to the csv file. Defaults to None, if not passed as an
        argument via the command line. Relative to root.

    """
    from app import init_import_dois_from_csv

    if not filename:
        filename = app.config['CSV_FILENAME']
    init_import_dois_from_csv(filename)


@app.cli.command()
def delete_init():
    """Create the doi Url's."""
    from app import delete_dois
    from app import delete_urls
    delete_urls()
    delete_dois()


@app.cli.command()
def create_doi_urls():
    """Create the doi Url's."""
    from app import create_doi_old_urls
    from app import create_doi_new_urls
    create_doi_old_urls()
    create_doi_new_urls()


@app.cli.command()
def create_doi_new_urls():
    """Create the doi Url's."""
    from app import create_doi_new_urls
    create_doi_new_urls()


@app.cli.command()
def create_doi_old_urls():
    """Create the doi Url's."""
    from app import create_doi_old_urls
    create_doi_old_urls()


@app.cli.command()
def create_doi_lp_urls():
    """Create the doi Url's."""
    from app import create_doi_lp_urls
    create_doi_lp_urls()


@app.cli.command()
def create_ncbi_urls():
    """Create the NCBI Url's."""
    from app import create_ncbi_urls
    create_ncbi_urls(app.config['NCBI_TOOL'], app.config['APP_EMAIL'])


@app.cli.command()
def create_unpaywall_urls():
    """Create the Unpaywall Url's."""
    from app import create_unpaywall_urls
    create_unpaywall_urls(app.config['APP_EMAIL'])


@app.cli.command()
def create_urls():
    """Create the Unpaywall Url's."""
    create_doi_old_urls()
    create_doi_new_urls()
    create_ncbi_urls()
    create_unpaywall_urls()


@app.cli.command()
def create_fbrequests():
    """Create the Facebook request."""
    from app import fb_requests
    fb_requests(app.config['FB_APP_ID'], app.config['FB_APP_SECRET'],
                app.config['FB_BATCH_SIZE'])


@app.cli.command()
def delete_dois():
    """Delete all entries in doi table."""
    from app import delete_dois
    delete_dois()


@app.cli.command()
def delete_urls():
    """Delete all entries in url table."""
    from app import delete_urls
    delete_urls()


@app.cli.command()
def delete_apirequests():
    """Delete all entries in url table."""
    from app import delete_apirequests
    delete_apirequests()


@app.cli.command()
def delete_fbrequests():
    """Delete all entries in fbrequests table."""
    from app import delete_fbrequests
    delete_fbrequests()


@app.cli.command()
def delete_data():
    """Create the doi Url's."""
    from app import delete_dois
    from app import delete_urls
    from app import delete_apirequests
    from app import delete_fbrequests
    delete_fbrequests()
    delete_apirequests()
    delete_urls()
    delete_dois()


@app.cli.command()
@click.argument('table_names')
def export_data(table_names):
    """Export tables passed as string, seperated by comma.

    Parameters
    ----------
    table_names : string
        String with table names, seperated by comma.

    """
    from app import export_tables_to_csv

    if not table_names:
        table_names = 'doi,url,api_request,fb_request'

    table_names = table_names.split(',')
    export_tables_to_csv(table_names, app.config['SQLALCHEMY_DATABASE_URI'])


@app.cli.command()
@click.argument('table_names', required=False)
def import_data(table_names, delete_tables=False):
    """Import data.

    table_names must be passed in the right order.
    e.g. 'doi,url,api_request,fb_request'

    Files must be available as:
        fb_request.csv, api_request.csv, doi.csv, url.csv

    Parameters
    ----------
    table_names : string
        String with table names, seperated by comma.

    """
    from app import import_csv

    if not table_names or table_names == '':
        table_names = ['doi', 'url', 'api_request', 'fb_request']
    else:
        table_names_tmp = [table_name.strip() for table_name in table_names.split(',')]
        table_names = table_names_tmp

    import_csv(table_names, delete_tables)


@app.route('/')
@app.route('/index')
def index():
    """Homepage."""
    return render_template('index.html', title='Home')


@app.route('/api')
@app.route('/api/v1')
def api():
    """Api page."""
    return render_template('api.html', title='API')


@app.route('/api/v1/add_data', methods=['POST', 'GET'])
def add_data():
    """Add data via an API endpoint to the database.

    Required: doi
    Optional: url, date
    """
    response_status = 'error'
    url_type_list = ['ojs', 'doi_new', 'doi_old', 'doi_new_landingpage', 'unpaywall', 'pubmed', 'pubmedcentral']

    if request.method == 'POST':
        try:
            if 'X-API-Key' in request.headers:
                if app.config['API_TOKEN'] == request.headers['X-API-Key']:
                    if request.headers['Content-Type'] == 'application/json':
                        data = request.json
                        if isinstance(data, list):
                            is_data_valid = True
                            for entry in data:
                                if 'doi' in entry:
                                    if not isinstance(entry['doi'], str):
                                        response = 'DOI {} is no string.'.format(entry['doi'])
                                        is_data_valid = False
                                    if 'url' in entry:
                                        if not isinstance(entry['url'], str):
                                            response = 'URL {} is no string.'.format(entry['url'])
                                            is_data_valid = False
                                        if 'url_type' in entry:
                                            if not isinstance(entry['url_type'], str):
                                                response = 'URL type {} is no string.'.format(entry['url_type'])
                                                is_data_valid = False
                                            if entry['url_type'] not in url_type_list:
                                                response = 'URL type {} is not one of the allowed types.'.format(entry['url_type'])
                                                is_data_valid = False
                                        else:
                                            response = 'URL type is missing.'
                                            is_data_valid = False
                                    if 'date' in entry:
                                        if not isinstance(entry['date'], str):
                                            response = 'Date {} is no string.'.format(entry['date'])
                                            is_data_valid = False
                                else:
                                    is_data_valid = False
                                    response = 'DOI is missing in {}.'.format(entry)
                            if is_data_valid:
                                resp_func = import_dois_from_api(data)
                                if resp_func:
                                    response = resp_func
                                    response_status = 'ok'
                                else:
                                    response = 'Error: JSON from API could not be stored in database.'
                        else:
                            response = 'No list of data in JSON.'
                    else:
                        response = 'No JSON delivered.'
                else:
                    response = 'Authentication token not right.'
            else:
                response = 'Authentication token not passed.'
        except:
            response = 'Undefined error.'

        return jsonify({'status': response_status, 'content': response})
    else:
        return jsonify({'status': 'on', 'api_version': '1.0'})
