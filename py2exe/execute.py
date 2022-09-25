from ui_to_py import main as ui
def setUi(class_link):
	form = ui()
	form.setupUi(class_link)
	print(form.__dict__)
	class_link.__dict__.update(form.__dict__)
	return class_link
