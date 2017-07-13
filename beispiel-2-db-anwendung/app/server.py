#!/usr/bin/env python3

import os
import codecs

import psycopg2
from http.server import BaseHTTPRequestHandler, HTTPServer


conn = psycopg2.connect("host={host} dbname={db} user={user} password={passwd}".format(
	host=os.environ['DB_HOST'],
	db=os.environ['DB_NAME'],
	user=os.environ['DB_USER'],
	passwd=os.environ['DB_PASS'],
))

cur = conn.cursor()
cur.execute("""
	CREATE TABLE IF NOT EXISTS reqs (
		id serial PRIMARY KEY,
		created timestamp not null default now(),
		ua varchar,
		ip varchar
	);
""")
print("created table if not existed")
print(conn.notices)

conn.commit()
cur.close()

class Handler(BaseHTTPRequestHandler):
	def ip(self):
		if 'X-Forwarded-For' in self.headers:
			addrs = self.headers['X-Forwarded-For'].split(',')
			return addrs[0].strip()

		return self.client_address[0]

	def ua(self):
		return self.headers['User-Agent']

	def do_GET(self):
		if self.path == '/favicon.ico':
			self.send_response(404)
			return

		self.log_request();
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		cur = conn.cursor()
		cur.execute("INSERT INTO reqs (ua, ip) VALUES (%s, %s)",
			(self.ua(), self.ip()))

		cur.execute("SELECT * FROM reqs")

		writer = codecs.getwriter("utf-8")(self.wfile);
		writer.write("""
		<!DOCTYPE html><html><body>
			<h1>Requests</h1>
			<p>
				<strong>You are</strong> <tt>{ua}</tt> <strong>from</strong> <tt>{ip}</tt>
			</p>
			<ul>
		""".format(
			ua=self.ua(),
			ip=self.ip()
		).strip())

		for row in cur:
			writer.write("<li>{row}</li>".format(
				row=row
			))

		writer.write("""
			</ul>
		</body></html>
		""".strip())

		conn.commit()
		cur.close()

server_address = ('', 5000)
httpd = HTTPServer(server_address, Handler)
httpd.serve_forever()
