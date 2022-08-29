# from io import BytesIO  # A stream implementation using an in-memory bytes buffer
# # It inherits BufferIOBase
#
# from django.http import HttpResponse
# from django.template.loader import get_template, render_to_string
#
# # pisa is a html2pdf converter using the ReportLab Toolkit,
# # the HTML5lib and pyPdf.
#
# from xhtml2pdf import pisa
#
#
# def convert_html_to_pdf(source_html, output_filename):
#     # open output file for writing (truncated binary)
#     result_file = open(output_filename, "w+b")
#
#     # convert HTML to PDF
#     pisa_status = pisa.CreatePDF(
#         source_html,  # the HTML to convert
#         dest=result_file)  # file handle to recieve result
#     print(pisa_status)
#     # close output file
#     result_file.close()  # close output file
#
#     # return False on success and True on errors
#     return pisa_status.err
#
#
# # define render_to_pdf() function
# def render_to_pdf(template_src, context_dict={}):
#     # template = get_template(template_src)
#     # html = template.render(context_dict)
#     print(context_dict)
#     html = render_to_string(template_src, context_dict).encode('utf-8')
#
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html), result, encoding='UTF-8')
#     print("aaaaaaaaaaaaaaaa")
#     converted = result.getvalue() if not pdf.err else print(pdf.err)
#     print(converted)
#     # print(html)
#     # result = BytesIO
#
#     # This part will create the pdf.
#     # pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
#     filename = 'Questionario-di-gradimento.pdf'
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename=%s' % filename
#     response.write(converted)
#     return response
