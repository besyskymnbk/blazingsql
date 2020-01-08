/*
 * Schema.h
 *
 *  Created on: Apr 26, 2019
 *      Author: felipe
 */

#ifndef BLAZING_RAL_SCHEMA_H_
#define BLAZING_RAL_SCHEMA_H_


#include "../GDFColumn.cuh"
#include <cudf/cudf.h>
#include <string>
#include <vector>


// TODO includes from BlazingTable
//#include <memory>
//#include <vector>
#include <string>
#include "cudf/table/table.hpp"
#include "cudf/table/table_view.hpp"
#include "cudf/column/column_view.hpp"

namespace ral {

// TODO all this namespace frame should be erased from here
namespace frame {
	typedef cudf::experimental::table CudfTable;
	typedef cudf::table_view CudfTableView;
	typedef cudf::column_view CudfColumnView;
class BlazingTable{
  	public:
  		BlazingTable(std::unique_ptr<CudfTable> table,std::vector<std::string> columnNames);
  		CudfTableView view() const;

			cudf::size_type num_columns() const {
				return table->num_columns();
			}

			cudf::size_type num_rows() const {
				return table->num_rows();
			}
  		std::vector<std::string> names() const;
  	private:
  		std::vector<std::string> columnNames;
  		std::unique_ptr<CudfTable> table;
};

class BlazingTableView{
  	public:
		BlazingTableView(CudfTableView table,std::vector<std::string> columnNames);
		CudfTableView view() const;
		std::vector<std::string> names() const;
  	private:
		std::vector<std::string> columnNames;
		CudfTableView table;
};

} // namespace frame

namespace io {

/**
 * I did not want to write this and its very dangerous
 * but the cudf::io::csv::reader_options (what a name) currently requires a char * input
 *I have no idea why
 */
std::string convert_dtype_to_string(const cudf::type_id & dtype);

class Schema {
public:
	Schema();

	Schema(std::vector<std::string> names,
		std::vector<size_t> calcite_to_file_indices,
		std::vector<cudf::type_id> types,
		std::vector<size_t> num_row_groups);

	Schema(std::vector<std::string> names,
		std::vector<size_t> calcite_to_file_indices,
		std::vector<cudf::type_id> types,
		std::vector<size_t> num_row_groups,
		std::vector<bool> in_file);

	Schema(std::vector<std::string> names, std::vector<cudf::type_id> types);

	virtual ~Schema();

	std::vector<std::string> get_names() const;
	std::vector<std::string> get_types() const;
	std::vector<std::string> get_files() const;
	std::vector<bool> get_in_file() const;
	std::vector<cudf::type_id> get_dtypes() const;
	std::string get_name(size_t schema_index) const;
	std::string get_type(size_t schema_index) const;
	std::vector<size_t> get_calcite_to_file_indices() const { return this->calcite_to_file_indices; }
	std::vector<size_t> get_num_row_groups() const { return this->num_row_groups; }
	Schema fileSchema() const;
	size_t get_file_index(size_t schema_index) const;

	size_t get_num_row_groups(size_t file_index) const;

	size_t get_num_columns() const;

	// DEPRECATED please use add_column(name, type, file_index, is_in_file)
	void add_column(gdf_column_cpp column, size_t file_index);
	
	void add_file(std::string file);

	void add_column(std::string name,
		cudf::type_id type,
		size_t file_index,
		bool is_in_file = true);

	inline bool operator==(const Schema & rhs) const {
		return (this->names == rhs.names) && (this->types == rhs.types);
	}

	inline bool operator!=(const Schema & rhs) { return !(*this == rhs); }

private:
	std::vector<std::string> names;
	std::vector<size_t> calcite_to_file_indices;  // maps calcite columns to our columns
	std::vector<cudf::type_id> types;
	std::vector<size_t> num_row_groups;
	std::vector<bool> in_file;
	std::vector<std::string> files;
};

} /* namespace io */
} /* namespace ral */

#endif /* BLAZING_RAL_SCHEMA_H_ */
