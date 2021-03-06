#!/usr/bin/env python3
import funct
import sql
from jinja2 import Environment, FileSystemLoader
env = Environment(extensions=["jinja2.ext.do"], loader=FileSystemLoader('templates/'), autoescape=True)
template = env.get_template('servers.html')
form = funct.form

print('Content-type: text/html\n')
funct.check_login()
funct.page_for_admin(level=2)
try:
	user, user_id, role, token, servers = funct.get_users_params()
	ldap_enable = sql.get_setting('ldap_enable')
	grafana, stderr = funct.subprocess_execute("service grafana-server status |grep Active |awk '{print $1}'")
	user_group = funct.get_user_group(id=1)
	settings = sql.get_setting('', all=1)
	geoip_country_codes = sql.select_geoip_country_codes()

	services = []
	services_name = {'checker_haproxy': 'Checker backends master service',}
	for s, v in services_name.items():
		cmd = "systemctl status %s |grep Act |awk  '{print $2}'" % s
		status, stderr = funct.subprocess_execute(cmd)
		if s != 'keep_alive':
			service_name = s.split('_')[0]
		else:
			service_name = s
		cmd = "rpm --query haproxy-wi-"+service_name+"-* |awk -F\""+service_name + "\" '{print $2}' |awk -F\".noa\" '{print $1}' |sed 's/-//1' |sed 's/-/./'"
		service_ver, stderr = funct.subprocess_execute(cmd)

		try:
			services.append([s, status, v, service_ver[0]])
		except Exception:
			services.append([s, status, v, ''])

except Exception as e:
	pass


output_from_parsed_template = template.render(title="Servers: ",
												role=role,
												user=user,
												users=sql.select_users(group=user_group),
												groups=sql.select_groups(),
												servers=sql.get_dick_permit(virt=1, disable=0),
												roles=sql.select_roles(),
												masters=sql.select_servers(get_master_servers=1, uuid=user_id.value),
												group=user_group,
												sshs=sql.select_ssh(group=user_group),
												telegrams=sql.get_user_telegram_by_group(user_group),
												token=token,
												settings=settings,
												backups=sql.select_backups(),
												grafana=''.join(grafana),
												page="servers.py",
												geoip_country_codes=geoip_country_codes,
											  	services=services,
												ldap_enable=ldap_enable)
print(output_from_parsed_template)
