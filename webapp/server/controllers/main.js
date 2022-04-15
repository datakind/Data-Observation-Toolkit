const getTableData = (req, res, db) => {

  db.select('*').from('dot.configured_tests')
    .then(items => {
      if(items.length){
        res.json(items)
      } else {
        res.json({dataExists: 'false'})
      }
    })
    .catch(err => res.status(400).json({dbError: 'db error'}))
}

const postTableData = (req, res, db) => {
  console.log("Received a POST request to insert data ...")
  console.log(req.body)

  let date_now = new Date();
  date_now = date_now.toISOString();

  const { test_activated, test_type, entity, column_name, description, test_parameters, custom_sql, test_id, date_added_client, date_modified_client, last_updated_by } = req.body
  date_added = date_now;
  date_modified = date_now;
  db('dot.configured_tests').insert({test_activated, test_id, date_added, date_modified, last_updated_by, entity, test_type, column_name, description, test_parameters, custom_sql})
    .returning('*')
    .then(item => {
      res.json(item)
    })
    .catch(err => res.status(400).json({dbError: 'db error'}))
}

const putTableData = (req, res, db) => {
  console.log("Received a PUT request to update data ...")
  console.log(req.body)
  const { test_activated, test_type, entity, column_name, description, test_parameters, custom_sql, test_id, date_added, date_modified_previous, last_updated_by } = req.body
  const date_modified = new Date()
  db('dot.configured_tests').where({test_id}).update({test_activated, test_id, date_added, date_modified, last_updated_by, entity, test_type, column_name, description, test_parameters, custom_sql})
    .returning('*')
    .then(item => {
      res.json(item)
    })
    .catch(err => res.status(400).json({dbError: 'db error'}))
}

const deleteTableData = (req, res, db) => {
  console.log("Received a DELETE request to update data ...")
  console.log(req.body)
  const { test_id } = req.body
  db('dot.configured_tests').where({test_id}).del()
    .then(() => {
      res.json({delete: 'true'})
    })
    .catch(err => res.status(400).json({dbError: 'db error'}))
}

module.exports = {
  getTableData,
  postTableData,
  putTableData,
  deleteTableData
}
