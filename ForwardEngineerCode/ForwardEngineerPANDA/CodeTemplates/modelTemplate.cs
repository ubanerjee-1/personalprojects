using System;
using System.ComponentModel.DataAnnotations;
using Purina.Panda.Common;
using System.Linq.Expressions;
using System.ComponentModel.DataAnnotations.Schema;
using Purina.Panda.Common.ModelInterfaces;
namespace Purina.Panda.ADD_SPECIE_NAME.Model.Models
{
    [Table("INSERT_TABLE_NAME")]
    public class INSERT_TABLE_NAME : IHasLastUpdated, IHasPrimaryKey<INSERT_TABLE_NAME>
    {
        public Expression<Func<INSERT_TABLE_NAME, object>> PrimaryKeyExpression => (e => new { INSERT_PRIMARY_KEY});
INSERT_COLUMN_LOGIC
    }
}
