import React, { useState } from 'react';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';


//I need to make it so tht the user can edit the company, position, or applied, adn add a new job manually. then teh top part shoudl go based on that. 

const columns = [
  { id: 'Company', label: 'Company', minWidth: 170, align: 'center' },
  { id: 'Position', label: 'Position', minWidth: 170, align: 'center' },
  { id: 'Status', label: 'Status', minWidth: 170, align: 'center' },
];

function createData(Company, Position, Status) {
  return { Company, Position, Status };
}

const rows = [
  createData('GrubHub', 'Software', 'Applied'),
  createData('TheHartford', 'Software', 'Interviewing'),
  createData('Apple', 'IT', 'Applied'),
  createData('Microsoft', 'Cyber', 'Interviewing'),
];

export default function StickyHeadTable() {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(+event.target.value);
    setPage(0);
  };

  return (
    <Paper sx={{ width: '80%', overflow: 'auto' , margin: '0 auto', boxShadow: 3, borderRadius: 2}}>
      <TableContainer sx={{ maxHeight: 440, overflowX: 'auto' , overflow: 'auto'}}>
        <Table stickyHeader aria-label="sticky table" size="small" sx={{ minWidth: 500 }}>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  style={{ minWidth: column.minWidth , fontWeight:'bold', background:'black', color:'white'}}
                >
                  {column.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((row, idx) => (
                <TableRow hover role="checkbox" tabIndex={-1} key={idx}>
                  {columns.map((column) => {
                    const value = row[column.id];
                    return (
                      <TableCell key={column.id} align={column.align || 'left'}>
                        {typeof value === 'number'
                          ? value.toLocaleString('en-US')
                          : value}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10, 25, 100]}
        component="div"
        count={rows.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
}
