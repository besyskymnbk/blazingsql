#include "utilities/TableWrapper.h"
#include "GDFColumn.cuh"

namespace ral {
namespace utilities {

TableWrapper::TableWrapper(const std::vector<gdf_column_cpp> & columns) {
	columns_.resize(columns.size());
	for(size_t i = 0; i < columns_.size(); ++i) {
		columns_[i] = columns[i].get_gdf_column();
	}
}

TableWrapper::TableWrapper(const std::vector<gdf_column_cpp> & columns, const std::vector<int> & colIndices) {
	columns_.resize(colIndices.size());
	for(size_t i = 0; i < columns_.size(); ++i) {
		columns_[i] = columns[colIndices[i]].get_gdf_column();
	}
}

cudf::column ** TableWrapper::getColumns() { return columns_.data(); }

cudf::size_type TableWrapper::getQuantity() { return columns_.size(); }

}  // namespace utilities
}  // namespace ral
