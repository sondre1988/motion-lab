function phi_tt = ode(in1,in2,in3,l,l_t,g)
%ODE
%    PHI_TT = ODE(IN1,IN2,IN3,L,L_T,G)

%    This function was generated by the Symbolic Math Toolbox version 8.0.
%    09-May-2018 14:03:56

phi1 = in1(1,:);
phi2 = in1(2,:);
phi_t1 = in2(1,:);
phi_t2 = in2(2,:);
pt_tt1 = in3(1,:);
pt_tt2 = in3(2,:);
pt_tt3 = in3(3,:);
t2 = cos(phi2);
t3 = sin(phi1);
t4 = cos(phi1);
t5 = 1.0./l;
t6 = sin(phi2);
phi_tt = [-t5.*(l_t.*phi_t1.*2.0-pt_tt1.*t4+g.*t2.*t3-pt_tt3.*t2.*t3-pt_tt2.*t3.*t6+l.*phi_t2.^2.*t3.*t4);-(t5.*(g.*t6+pt_tt2.*t2-pt_tt3.*t6+l_t.*phi_t2.*t4.*2.0-l.*phi_t1.*phi_t2.*t3.*2.0))./t4];
