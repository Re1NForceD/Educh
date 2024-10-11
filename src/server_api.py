import logging
import server_api
import server_logic
import server_storage


if __name__ == "__main__":
  # TODO: form config from env
  storage_config = {
      "db_host": "localhost",
      "db_port": "3306",
      "db_name": "educh_db",
      "db_user": "root",
      "db_password": "12345"
  }
  api_config = {"TEST": 666}
  logic_config = {"TEST": 666}

  storage_module = server_storage.MySQLStorage(storage_config)
  comm_module = server_api.app.FlaskApp(api_config)
  logic_module = server_logic.Logic(logic_config, storage_module, comm_module)

  comm_module.set_logic(logic_module)
  comm_module.start()
