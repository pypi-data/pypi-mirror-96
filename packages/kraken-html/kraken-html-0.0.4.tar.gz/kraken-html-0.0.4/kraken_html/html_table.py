
class Html_table:

    def __init__(self):
        a=1

    def table(self, keys, value):


        content = ''
        content += '<table class="table">'
        content += self._table_header(keys, value) 
        content += self._table_body(keys, value) 
        content += '</table>'


        return content


    def _table_header(self, keys, value):

        # Error handling
        if not keys:
            return ''

        content = ''
        content += self._table_header_init()
        content += self._table_header_row(keys, value)
        content += self._table_header_close()


        return content



    def _table_header_init(self):

        return '<thead class="thead-dark">'



    def _table_header_row(self, keys, value):

        content = ''
        content += '<tr>'

        # Iterate through keys 
        for i in keys:
            content += self._table_header_cell(i)

        content += '</tr>'


        return content


    def _table_header_cell(self, value):

        content = '<th>{value}</th>'.format(value=value)

        return content


    def _table_header_close(self):

        content = '</thead>'

        return content




    def _table_body(self, keys, value):

        content = ''
        content += self._table_body_init()

        for i in value:
            content += self._table_body_row(keys, i)
        
        
        content += self._table_body_close()

        return content



    def _table_body_init(self):

        content = '</tbody>'

        return content



    def _table_body_row(self, keys, value):


        content = ''
        content += '<tr>'

        # Iterate through keys 
        for i in keys:
            cell_value = value.get(i, None)
            content += self._table_body_cell(cell_value)

        content += '</tr>'


        return content



    def _table_body_cell(self, value):
        
        
        content = '<td>{value}</td>'.format(value=value)

        return content


    def _table_body_close(self):

        content = '</tbody>'

        return content
        

