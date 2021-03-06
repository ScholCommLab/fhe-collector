import click
from json import dumps, loads
from flask import jsonify
from flask import render_template
from flask import request
from app import create_app
from app import import_dois_from_csv

app = create_app()
app.app_context().push()


# TODO: show progress of api requests in shell
@app.cli.command()
def setup_db():
    """Insert raw data and pre-processed data to database.

    Command for shell execution.

    """
    import_dois_from_csv()
    create_doi_urls()
    create_ncbi_urls()
    create_unpaywall_urls()


@app.cli.command()
def delete_db():
    """Delete all database entries.

    Command for shell execution.

    """
    delete_fbrequests()
    delete_urls()
    delete_dois()


@app.cli.command()
def reset_import():
    """Reset database setup.

    Command for shell execution.

    """
    delete_urls()
    delete_dois()
    import_from_csv()


@app.cli.command()
def reset_db():
    delete_db()
    setup_db()


@app.cli.command()
@click.argument('filename', type=click.Path(exists=True), required=False)
def import_data(filename=None):
    """Import raw data from csv file.

    The filepath can be manually passed with the argument `filename`.

    Parameters
    ----------
    filename : string
        Filepath to the csv file. Defaults to None, if not passed as an
        argument via the command line.

    """
    from app import import_dois_from_csv

    if not filename:
        filename = app.config['CSV_FILENAME']
    import_dois_from_csv(filename)


@app.cli.command()
def create_doi_urls():
    """Create the doi Url's.

    """
    from app import create_doi_urls
    create_doi_urls()


@app.cli.command()
def create_ncbi_urls():
    """Create the NCBI Url's.

    """
    from app import create_ncbi_urls
    create_ncbi_urls(app.config['NCBI_TOOL'], app.config['APP_EMAIL'])


@app.cli.command()
def create_unpaywall_urls():
    """Create the Unpaywall Url's.

    """
    from app import create_unpaywall_urls
    create_unpaywall_urls(app.config['APP_EMAIL'])


@app.cli.command()
def create_fbrequests():
    """Create the Facebook request."""
    from app import fb_requests
    fb_requests(app.config['FB_APP_ID'], app.config['FB_APP_SECRET'],
                app.config['FB_BATCH_SIZE'])


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
@click.argument('table_names')
def export_tables(table_names):
    """Short summary.

    Parameters
    ----------
    table_names : string
        String with table names, seperated by comma.

    """
    from app import export_tables_to_csv

    table_names = table_names.split(',')
    export_tables_to_csv(table_names, app.config['SQLALCHEMY_DATABASE_URI'])


@app.cli.command()
@click.argument('table_names')
def import_tables(table_names):
    """Import data.

    The table_names will be sorted, from doi -> url -> fb_request.

    Parameters
    ----------
    table_names : string
        String with table names, seperated by comma.

    """
    from app import delete_dois
    from app import delete_fbrequests
    from app import delete_urls
    from app import import_tables_from_csv

    table_names_tmp = [table_name.strip() for table_name in table_names.split(',')]
    table_names = []
    if 'doi' in table_names_tmp:
        table_names.append('doi')
    if 'url' in table_names_tmp:
        table_names.append('url')
    if 'fb_request' in table_names_tmp:
        table_names.append('fb_request')

    for table_name in reversed(table_names):
        if table_name == 'doi':
            try:
                delete_dois()
            except:
                raise
        if table_name == 'url':
            try:
                delete_urls()
            except:
                raise
        if table_name == 'fb_request':
            try:
                delete_fbrequests()
            except:
                raise
    import_tables_from_csv(table_names, app.config['SQLALCHEMY_DATABASE_URI'])


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/api')
@app.route('/api/v1')
def api():
    return render_template('api.html', title='API')


@app.route('/api/v1/add_data', methods=['POST', 'GET'])
def add_data():
    """Add data to database.

    Required: doi
    Optional: url, date
    """
    response_status = 'error'
    url_type_list = ['ojs', 'doi_new', 'doi_old', 'doi_new_landingpage', 'unpaywall', 'pubmed', 'pubmedcentral']

    if request.method == 'POST':
        try:
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
                        resp_func = import_dois_from_csv(data)
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

        return jsonify({'status': response_status, 'content': response})
    else:
        return jsonify({'status': 'on', 'api_version': '1.0'})
