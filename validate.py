import sublime, sublime_plugin, urllib, json, re, threading

class ValidateKrlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.waiting = True
		self.status_message = 'Validating KRL...'
		t = threading.Thread(target=self.validate)
		t.start()
		self.update_status()

	def update_status(self):
		if not self.waiting:
			return;
		self.status_message += '.'
		sublime.status_message(self.status_message)
		sublime.set_timeout(self.update_status, 500)

	def validate(self):
		# Clear squiggly lines
		self.view.erase_regions('validate_errors')
		self.errors = []

		# Make request to KRL validate web service
		krl = self.view.substr(sublime.Region(0, self.view.size()))
		url = 'http://cs.kobj.net/manage/validate/'
		values = urllib.parse.urlencode({'rule': krl, 'flavor': 'json'})
		try:
			response = urllib.request.urlopen(url, values.encode('latin-1')).read().decode('utf-8')
		except urllib.error.HTTPError:
			sublime.status_message('KRL Validator: HTTP error')
			return
		finally:
			self.waiting = False

		# The response uses a couple of single quotes, so it isn't valid JSON. Replace
		# with double quotes and parse JSON.
		response = response.replace("'status' : 'success'", '"status" : "success"')
		response = response.replace("'result' :", '"result" :')
		data = json.loads(response)

		if data['status'] == 'success':
			sublime.status_message('Valid KRL')
			print('Valid KRL')

		if data['status'] == 'error':
			sublime.status_message('KRL not valid')
			
			regions = []
			menuitems = []
			self.errors = []

			for line in data['result'].splitlines():
				m = re.match('line (\d+):(\d+) (.*)', line)
				lineNo = m.group(1)
				columnNo = m.group(2)
				description = m.group(3)

				text_point = self.view.text_point(int(lineNo) - 1, int(columnNo) - 1)
				region = self.view.word(text_point)

				menuitems.append(lineNo + ':' + columnNo + ' ' + description)
				regions.append(region)
				self.errors.append((region, description))
				
			self.add_regions(regions)
			self.view.window().show_quick_panel(menuitems, self.on_chosen)

	def add_regions(self, regions):
		self.view.add_regions('validate_errors', regions, 'keyword', '',
			sublime.DRAW_EMPTY |
			sublime.DRAW_NO_FILL |
			sublime.DRAW_NO_OUTLINE |
			sublime.DRAW_SQUIGGLY_UNDERLINE |
			sublime.HIDE_ON_MINIMAP)

	def on_chosen(self, index):
		if index == -1:
			return

		# Focus the user requested region from the quick panel.
		region = self.errors[index][0]
		region_cursor = sublime.Region(region.begin(), region.begin())
		selection = self.view.sel()
		selection.clear()
		selection.add(region_cursor)
		self.view.show(region_cursor)
