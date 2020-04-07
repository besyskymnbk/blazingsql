#include "OrcParser.h"
#include <blazingdb/io/Util/StringUtil.h>

#include <arrow/io/file.h>

#include "../Schema.h"

#include <cudf/table/table.hpp>
#include <cudf/io/functions.hpp>
#include <blazingdb/io/Library/Logging/Logger.h>
#include <cudf/types.hpp>

#include <numeric>

namespace ral {
namespace io {

orc_parser::orc_parser(cudf::experimental::io::read_orc_args arg_) : orc_args{arg_} {}

orc_parser::~orc_parser() {
	// TODO Auto-generated destructor stub
}

cudf_io::table_with_metadata get_new_orc(cudf_io::read_orc_args orc_arg, 
	std::shared_ptr<arrow::io::RandomAccessFile> arrow_file_handle,
	bool first_row_only = false){

	orc_arg.source = cudf_io::source_info(arrow_file_handle);
	
	if (first_row_only) 
		orc_arg.num_rows = 1;

	cudf_io::table_with_metadata table_out = cudf_io::read_orc(orc_arg);

	arrow_file_handle->Close();

	return std::move(table_out);
}

std::unique_ptr<ral::frame::BlazingTable> orc_parser::parse(
	std::shared_ptr<arrow::io::RandomAccessFile> file,
	const std::string & user_readable_file_handle, // TODO where is this param used?
	const Schema & schema,
	std::vector<size_t> column_indices) {

	if(file == nullptr) {
		return nullptr;
	}
	
	cudf::experimental::io::read_orc_args new_orc_args = this->orc_args;
	if(column_indices.size() > 0) {
		new_orc_args.columns.resize(column_indices.size());
		
		for(size_t column_i = 0; column_i < column_indices.size(); column_i++) {
			new_orc_args.columns[column_i] = schema.get_name(column_indices[column_i]);
		}

		cudf_io::table_with_metadata orc_table = get_new_orc(new_orc_args, file);

		if(orc_table.tbl->num_columns() <= 0)
			Library::Logging::Logger().logWarn("orc_parser::parse no columns were read");

		return std::make_unique<ral::frame::BlazingTable>(std::move(orc_table.tbl), orc_table.metadata.column_names);		
	}
	return nullptr;
}

std::unique_ptr<ral::frame::BlazingTable> orc_parser::parse_batch(
	std::shared_ptr<arrow::io::RandomAccessFile> file,
	const std::string & user_readable_file_handle,
	const Schema & schema,
	std::vector<size_t> column_indices,
	size_t stripe)
{
	if(file == nullptr) {
		return schema.makeEmptyBlazingTable(column_indices);
	}
	if(column_indices.size() > 0) {
		// Fill data to orc_args
		cudf_io::read_orc_args orc_args{cudf_io::source_info{file}};

		orc_args.columns.resize(column_indices.size());

		for(size_t column_i = 0; column_i < column_indices.size(); column_i++) {
			orc_args.columns[column_i] = schema.get_name(column_indices[column_i]);
		}
		std::vector<int> consecutive_stripe_start;
		std::vector<int> consecutive_stripe_length;
		std::tie(consecutive_stripe_start, consecutive_stripe_length) = get_groups(schema);

		orc_args.stripe = consecutive_stripe_start[stripe];
		orc_args.stripe_count = consecutive_stripe_length[stripe];
		auto result = cudf_io::read_orc(orc_args);
		return std::make_unique<ral::frame::BlazingTable>(std::move(result.tbl), result.metadata.column_names);
	}
	return nullptr;
}

void orc_parser::parse_schema(
	std::vector<std::shared_ptr<arrow::io::RandomAccessFile>> files, ral::io::Schema & schema) {
	
	cudf_io::table_with_metadata table_out = get_new_orc(orc_args, files[0], true);
	assert(table_out.tbl->num_columns() > 0);

	for(cudf::size_type i = 0; i < table_out.tbl->num_columns() ; i++) {
		std::string name = table_out.metadata.column_names[i];
		cudf::type_id type = table_out.tbl->get_column(i).type().id();
		size_t file_index = i;
		bool is_in_file = true;
		schema.add_column(name, type, file_index, is_in_file);
	}
}

} /* namespace io */
} /* namespace ral */
