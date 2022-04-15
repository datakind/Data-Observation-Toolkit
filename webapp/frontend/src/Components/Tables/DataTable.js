import React from 'react'
import { v4 as uuidv4 } from 'uuid';
import { Input } from 'reactstrap';
import { Checkmark } from 'react-checkmark';

import CRUDTable,
{
  Fields,
  Field,
  CreateForm,
  UpdateForm,
  DeleteForm,
  Pagination
} from 'react-crud-table';

function DataTableCRUD(props) {

    const API_SERVER = process.env.REACT_APP_API_SERVER;
    console.log("API SERVER: " + API_SERVER);

    const TextAreaRenderer = ({ field }) => <textarea {...field} />;

    const TestActivatedRenderer = ({ field }) => {
      return( <Input
                      type="checkbox"
                      name="test_activated"
                      id="test_activated"
                      onChange={field.onChange}
                      checked={field.value === undefined ? true : field.value}
                    />);
    }

    const TestActivatedResolver = (test) => {
      console.log(test)
      let status = test.test_activated === undefined ? '' : test.test_activated === true ? 'ON':''
      if (status === 'ON') {
          return(<Checkmark size='medium' color='blue' /> );
      }
      return(status);
    }

    const EntityRenderer = ({ field }) => {
        return(
          <select
            name="entity"
            id="rntity"
            value={field.value}
            onChange={field.onChange}
          >
            <option value="not_set"></option>
            <option value="assessment">Assessment</option>
            <option value="assessment_follow_up">Assessment Followup</option>
            <option value="delivery">Delivery</option>
            <option value="family_planning_follow_up">Family Planning Followup</option>
            <option value="family_planning_registration">Family Planning Registration</option>
            <option value="household_visit">Household Visit</option>
            <option value="malnutrition_follow_up">Malnutrition Followup</option>
            <option value="malnutrition_registration">Malnutrition Registration</option>
            <option value="postnatal_follow_up">Postnatal Followup</option>
            <option value="pregnancy">Pregancy</option>
            <option value="pregnancy_danger_sign">Pregnancy Danger Sign</option>
            <option value="pregnancy_follow_up">Pregnancy Followup</option>
          </select>
        );
    }

    const TestTypeRenderer = ({ field }) => {
        return(
          <select
            name="test_type"
            id="test_type"
            value={field.value}
            onChange={field.onChange}
          >
            <option value="not_set"></option>
            <option value="accepted_values">Accepted Values</option>
            <option value="associated_columns_not_null">Associated Columns Not Null</option>
            <option value="custom_sql">Custom SQL</option>
            <option value="not_negative_string_column">Not Negative String Column</option>
            <option value="not_null">Not Null</option>
            <option value="relationship">Relationships</option>
            <option value="unique">Unique</option>
          </select>
        );
    }

    let tests = props.items;

    const SORTERS = {
      NUMBER_ASCENDING: mapper => (a, b) => mapper(a) - mapper(b),
      NUMBER_DESCENDING: mapper => (a, b) => mapper(b) - mapper(a),
      STRING_ASCENDING: mapper => (a, b) => mapper(a).localeCompare(mapper(b)),
      STRING_DESCENDING: mapper => (a, b) => mapper(b).localeCompare(mapper(a)),
    };

    const getSorter = (data) => {
      const mapper = x => x[data.field];
      let sorter = SORTERS.STRING_ASCENDING(mapper);

      if (data.field === 'id') {
        sorter = data.direction === 'ascending' ?
          SORTERS.NUMBER_ASCENDING(mapper) : SORTERS.NUMBER_DESCENDING(mapper);
      } else {
        sorter = data.direction === 'ascending' ?
          SORTERS.STRING_ASCENDING(mapper) : SORTERS.STRING_DESCENDING(mapper);
      }
      return sorter;
    };

    // TODO, where we might implement field validation
    //const validate_test = (test) => {
    //    const errors = {};
    //    if(test.test_type === "not_null" && !test.test_parameters) {
    //        errors.title = 'Please provide test parameters';
    //        console.log(errors);
    //        return false
    //    }
    //    return true;
    //}

    const service = {
      fetchItems: payload => {
        const { activePage, itemsPerPage } = payload.pagination;
        const start = (activePage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        let result = Array.from(tests);
        result = result.sort(getSorter(payload.sort));
        return Promise.resolve(result.slice(start, end));
      },
      fetchTotal: payload => {
        return Promise.resolve(tests.length);
      },
      create: (test) => {
        let date_now = new Date();
        date_now = date_now.toISOString();

        // validate_test(test);

        test.test_activated = test.test_activated === undefined ? true : test.test_activated;
        test.test_type = test.test_type === undefined ? '' : test.test_type;
        test.entity = test.entity === undefined ? '' : test.entity;
        test.column_name = test.column_name === undefined ? '' : test.column_name;
        test.description = test.description === undefined ? '' : test.description;
        test.test_parameters = test.test_parameters === undefined ? '' : test.parameters;
        test.custom_sql = test.custom_sql === undefined ? '' : test.custom_sql;
        test.last_updated_by = test.last_updated_by === undefined ? '' : test.last_updated_by;

        test.test_id = uuidv4();
        test.date_added = date_now;
        test.date_modified = date_now;

        tests.push({
            ...test
        });

        const submitAdd = e => {
            fetch(API_SERVER, {
              method: 'post',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  test_activated: test.test_activated,
                  test_type: test.test_type,
                  entity: test.entity,
                  column_name: test.column_name,
                  description: test.description,
                  test_parameters: test.test_parameters,
                  custom_sql: test.custom_sql,
                  test_id: test.test_id,
                  date_added: test.date_added,
                  date_modified: test.date_modified,
                  last_updated_by: test.last_updated_by
              })
            })
          .then(response => response.json())
          .then(item => {
            if(Array.isArray(item)) {
              console.log(test)
            } else {
              console.log('failure')
            }
          })
          .catch(err => console.log(err))
        };
        submitAdd(test);
        console.log(test);
        return Promise.resolve(test);
      },
      update: (data) => {
        const test = tests.find(t => t.test_id === data.test_id);

        let date_now = new Date();
        date_now = date_now.toISOString();

        test.test_activated = data.test_activated;
        test.test_type = data.test_type;
        test.entity = data.entity;
        test.column_name = data.column_name;
        test.description = data.description;
        test.test_parameters = data.test_parameters;
        test.custom_sql = data.custom_sql;
        test.test_id = data.test_id;
        test.date_added = data.date_added;
        test.date_modified = date_now;
        test.last_updated_by = data.last_updated_by;

        const submitFormEdit = e => {
            fetch(API_SERVER, {
              method: 'put',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  test_activated: data.test_activated,
                  test_type: data.test_type,
                  entity: data.entity,
                  column_name: data.column_name,
                  description: data.description,
                  test_parameters: data.test_parameters,
                  custom_sql: data.custom_sql,
                  test_id: data.test_id,
                  date_added: data.date_added,
                  date_modified: data.date_modified,
                  last_updated_by: data.last_updated_by
              })
            })
          .then(response => response.json())
          .then(item => {
            if(Array.isArray(item)) {
              console.log(test)
            } else {
              console.log('failure')
            }
          })
          .catch(err => console.log(err))
        };
        submitFormEdit(test);
        return Promise.resolve(test);
      },
      delete: (data) => {
        const test = tests.find(t => t.test_id === data.test_id);
        tests = tests.filter(t => t.test_id !== test.test_id);
        const submitDelete = e => {
          fetch(API_SERVER, {
              method: 'delete',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                test_id: data.test_id,
              })
          })
          .then(response => response.json())
          .then(item => {
            if(Array.isArray(item)) {
              console.log(test)
            } else {
              console.log('failure')
            }
          })
          .catch(err => console.log(err))
        }
        submitDelete(test);
        return Promise.resolve(test);
      },
    };

    const styles = {
      container: { margin: 'auto', width: 'fit-content' },
    };

    const CRUDTableOutput = () => (
      <div style={styles.container}>
          <CRUDTable
            //caption="Tests"
            fetchItems={payload => service.fetchItems(payload)}
          >
          <Fields>
            <Field
              name="test_activated"
              label="Test Activated"
              tableValueResolver = {TestActivatedResolver}
              render={TestActivatedRenderer}
            />
            <Field
              name="test_id"
              label="Id"
              hideInCreateForm
              readOnly
            />
            <Field
              name="test_type"
              label="Test Type"
              render={TestTypeRenderer}
            />
            <Field
              name="entity"
              label="Entity"
              placeholder="DOT Entity"
              render={EntityRenderer}
            />
            <Field
              name="description"
              label="Column Description"
              placeholder="Description"
            />
            <Field
              name="test_parameters"
              label="Test Parameters (separated with '|') "
              placeholder="Test Parameters"
              render={TextAreaRenderer}
            />
            <Field
              name="custom_sql"
              label="Custom SQL"
              placeholder="Custom SQL"
              render={TextAreaRenderer}
            />
            <Field
              name="date_added"
              label="Date Added"
              placeholder="Date Added"
              hideInCreateForm
            />
            <Field
              name="date_modified"
              label="Date Modified"
              placeholder="Date Modified"
              hideInCreateForm
            />
            <Field
              name="last_updated_by"
              label="Last Updated By"
              placeholder="Last Updated By"
            />
          </Fields>
          <CreateForm
            title="Test Creation"
            message=""
            trigger="Create Test"
            onSubmit={test => service.create(test)}
            submitText="Create"
            validate={(values) => {
              const errors = {};
              if (!values.test_type) {
                errors.title = 'Please provide test type';
              }
              console.log(errors);
              return errors;
            }}
          />

          <UpdateForm
            title="Update Test"
            message=""
            trigger="Update"
            onSubmit={test => service.update(test)}
            submitText="Update"
            validate={(values) => {
              const errors = {};
              if (!values.test_type) {
                errors.title = 'Please provide test type';
              }
              console.log(errors);
              return errors;
            }}
          />

          <DeleteForm
            title="Test Delete Process"
            message="Are you sure you want to delete the test?"
            trigger="Delete"
            onSubmit={test => service.delete(test)}
            submitText="Delete"
            validate={(values) => {
              const errors = {};
              if (!values.test_id) {
                errors.test_id = 'Please provide id';
              }
              return errors;
            }}
          />
          <Pagination
            itemsPerPage={10}
            fetchTotalOfItems={payload => service.fetchTotal(payload)}
          />
        </CRUDTable>
      </div>
    );
    CRUDTableOutput.propTypes = {};
    return(<CRUDTableOutput/>)
};


export default DataTableCRUD
