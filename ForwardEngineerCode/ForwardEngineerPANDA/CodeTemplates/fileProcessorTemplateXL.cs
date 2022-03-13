using Purina.Panda.ADD_SPECIE_NAME.Model.Models;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Purina.Panda.Common.FileProcessingBase;
using Purina.Panda.Common.FileReaders; 
using Purina.Panda.Common.DataTypeUtilities;
using Purina.Panda.Common.SharedModel.Models;

namespace Purina.Panda.ADD_SPECIE_NAME.FileProcessing.FileProcessors
{
    public class ADD_TABLE_NAMEProcessor : FileProcessorBulkCopyBase
    {
DEFINE_COLUMN_INDEX_VARIABLES

DEFINE_ACCEPTABLE_DATE_FORMATS

DEFINE_PIVOT_HEADER_VARIABLES
		
        public ADD_TABLE_NAMEProcessor(Stream input, string blobPath, string tableName, string funcId) : base(input, blobPath, tableName, funcId)
        {

        }
        
        public override async Task<List<TableStatus>> ProcessFile()
        {
            Columns = new string[] { ADD_ALL_COLUMN_NAMES_LIST };

            var records = ExcelFile.GetAllRecords(Input, "XL_SHEET_NAME");
			
			SET_HEADER_VARIABLE
			
GET_PIVOT_HEADER_LIST
			
            records = records.Skip(NON_DATA_ROWS);
FOOTER_FILTER            records = records.Where(r => Enumerable.Range(0, NUM_COLUMNS_IN_FILE).Any(ix => !String.IsNullOrWhiteSpace(r.ElementAt(ix))));
            
ASSIGN_COLUMN_INDEX_VARIABLES


            ConvertRecords(RECORDS_VARABLEs, record => AddRecord(recordADDITIONALARGUMENTSCALL));

            await DeletePreviousFileRecords();

            await CommitRecords();

            return TableStatuses;
        }
        
        private void AddRecord(IEnumerable<string> recordADDITIONALARGUMENTSDEFINITION)
EXTRA_INDENT		{
PIVOT_LOOP_START	
EXTRA_INDENT            entries.Rows.Add(
ADD_COLUMN_DATA_MAPPINGS
EXTRA_INDENT            );
PIVOT_LOOP_END
        }
    }
}
