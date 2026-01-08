//////////////// half adder
module half_adder (
    input a,b,
    output sum,carry
  );

  assign sum = a ^ b;
  assign carry = a & b;

endmodule

//////////////// full adder

module full_adder(
    input a,b,cin,
    output sum,carry
  );

  wire c,c1,s;

  half_adder ha0(a,b,s,c);
  half_adder ha1(cin,s,sum,c1);

  assign carry = c | c1 ;

endmodule

//////////////////// 4-bit Ripple carry adder

module top(
    input [3:0] a,b,
    input [3:0] sout,
    input cin,
    output cout
  );

  wire c0,c1,c2;

  full_adder f0 (a[0], b[0], cin,sout[0], c0);
  full_adder f1 (a[1], b[1], c0, sout[1], c1);
  full_adder f2 (a[2], b[2], c1, sout[2], c2);
  full_adder f3 (a[3], b[3], c2, sout[3], cout);



  initial
  begin
    $dumpfile("rca4bit.vcd");
    $dumpvars(1,top);
  end



endmodule
