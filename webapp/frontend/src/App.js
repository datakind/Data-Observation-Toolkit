import React, { useState, useEffect } from 'react'
import { Container, Row, Col } from 'reactstrap'
import DataTableCRUD from './Components/Tables/DataTable'

//import { CSVLink } from "react-csv"

function App(props) {

  const [items, setItems] = useState([])

  require('dotenv').config()
  const API_SERVER = process.env.REACT_APP_API_SERVER;

  console.log(API_SERVER);

  const getItems= () => {
    fetch(API_SERVER)
      .then(response => response.json())
      .then(items => setItems(items))
      .catch(err => console.log(err))
  }

  useEffect(() => {
    getItems()
  }, []);

  //return (
  //    <Container className="App">
  //      <Row>
  //        <Col>
  //          <h1 style={{margin: "20px 0"}}>Configured Tests</h1>
  //        </Col>
  //      </Row>
  //      <Row>
  //        <Col>
  //          <DataTableCRUD items={items} updateState={updateState} deleteItemFromState={deleteItemFromState} />
  //        </Col>
  //      </Row>
  //      <Row></Row>
  //      <Row>
  //        <Col>
  //          <CSVLink
  //            filename={"db.csv"}
  //            color="primary"
  //            style={{float: "left", marginRight: "10px"}}
  //            className="btn btn-primary"
  //            data={items}>
  //            Download CSV
  //          </CSVLink>
  //        </Col>
  //      </Row>
  //    </Container>
  //)

    return (
      <Container className="App">
        <Row>
          <Col>
            <h1 style={{margin: "20px 0"}}>Configured Tests</h1>
          </Col>
        </Row>
        <Row>
          <Col>
            <DataTableCRUD items={items} showQueryBuilder />
          </Col>
        </Row>
      </Container>
  )

}

export default App
