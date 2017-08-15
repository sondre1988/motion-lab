// Pybind includes
#include <pybind11/pybind11.h>

// Classes
#include "UdpServer.h"
#include "RemoteInterface.h"
#include "HmiInterface.h"




namespace py = pybind11;

PYBIND11_PLUGIN(MotionLab) {
	// Module
	py::module m("MotionLab", "Udp server and client utilites");

	// Feedback structs
	py::class_<RemoteFeedbackStewart>(m, "RemoteFeedbackStewart")
		.def(py::init<>())
		.def_readonly("x", &RemoteFeedbackStewart::x)
		.def_readonly("y", &RemoteFeedbackStewart::y)
		.def_readonly("z", &RemoteFeedbackStewart::z)
		.def_readonly("roll", &RemoteFeedbackStewart::roll)
		.def_readonly("pitch", &RemoteFeedbackStewart::pitch)
		.def_readonly("yaw", &RemoteFeedbackStewart::yaw)
		.def_readonly("x_t", &RemoteFeedbackStewart::x_t)
		.def_readonly("y_t", &RemoteFeedbackStewart::y_t)
		.def_readonly("z_t", &RemoteFeedbackStewart::z_t)
		.def_readonly("roll_t", &RemoteFeedbackStewart::roll_t)
		.def_readonly("pitch_t", &RemoteFeedbackStewart::pitch_t)
		.def_readonly("yaw_t", &RemoteFeedbackStewart::yaw_t)
		.def_readonly("x_tt", &RemoteFeedbackStewart::x_tt)
		.def_readonly("y_tt", &RemoteFeedbackStewart::y_tt)
		.def_readonly("z_tt", &RemoteFeedbackStewart::z_tt)
		.def_readonly("roll_tt", &RemoteFeedbackStewart::roll_tt)
		.def_readonly("pitch_tt", &RemoteFeedbackStewart::pitch_tt)
		.def_readonly("yaw_tt", &RemoteFeedbackStewart::yaw_tt)
		.def_readonly("L1", &RemoteFeedbackStewart::L1)
		.def_readonly("L2", &RemoteFeedbackStewart::L2)
		.def_readonly("L3", &RemoteFeedbackStewart::L3)
		.def_readonly("L4", &RemoteFeedbackStewart::L4)
		.def_readonly("L5", &RemoteFeedbackStewart::L5)
		.def_readonly("L6", &RemoteFeedbackStewart::L6);

	py::class_<RemoteFeedbackComau>(m, "RemoteFeedbackComau")
		.def(py::init<>())
		.def_readonly("q1", &RemoteFeedbackComau::q1)
		.def_readonly("q2", &RemoteFeedbackComau::q2)
		.def_readonly("q3", &RemoteFeedbackComau::q3)
		.def_readonly("q4", &RemoteFeedbackComau::q4)
		.def_readonly("q5", &RemoteFeedbackComau::q5)
		.def_readonly("q6", &RemoteFeedbackComau::q6)
		.def_readonly("q1_t", &RemoteFeedbackComau::q1_t)
		.def_readonly("q2_t", &RemoteFeedbackComau::q2_t)
		.def_readonly("q3_t", &RemoteFeedbackComau::q3_t)
		.def_readonly("q4_t", &RemoteFeedbackComau::q4_t)
		.def_readonly("q5_t", &RemoteFeedbackComau::q5_t)
		.def_readonly("q6_t", &RemoteFeedbackComau::q6_t)
		.def_readonly("q1_tt", &RemoteFeedbackComau::q1_tt)
		.def_readonly("q2_tt", &RemoteFeedbackComau::q2_tt)
		.def_readonly("q3_tt", &RemoteFeedbackComau::q3_tt)
		.def_readonly("q4_tt", &RemoteFeedbackComau::q4_tt)
		.def_readonly("q5_tt", &RemoteFeedbackComau::q5_tt)
		.def_readonly("q6_tt", &RemoteFeedbackComau::q6_tt);

	py::class_<RemoteFeedbackLeica>(m, "RemoteFeedbackLeica")
		.def(py::init<>())
		.def_readonly("x", &RemoteFeedbackLeica::x)
		.def_readonly("y", &RemoteFeedbackLeica::y)
		.def_readonly("z", &RemoteFeedbackLeica::z)
		.def_readonly("q0", &RemoteFeedbackLeica::q0)
		.def_readonly("q1", &RemoteFeedbackLeica::q1)
		.def_readonly("q2", &RemoteFeedbackLeica::q2)
		.def_readonly("q3", &RemoteFeedbackLeica::q3);

	py::class_<RemoteFeedbackMru>(m, "RemoteFeedbackMru")
		.def(py::init<>())
		.def_readonly("heave",&RemoteFeedbackMru::heave)
		.def_readonly("heave_t",&RemoteFeedbackMru::heave_t)
		.def_readonly("heave_tt",&RemoteFeedbackMru::heave_tt)
		.def_readonly("turn_rate",&RemoteFeedbackMru::turn_rate)
		.def_readonly("roll",&RemoteFeedbackMru::roll)
		.def_readonly("pitch",&RemoteFeedbackMru::pitch)
		.def_readonly("yaw",&RemoteFeedbackMru::yaw)
		.def_readonly("wx",&RemoteFeedbackMru::wx)
		.def_readonly("wy",&RemoteFeedbackMru::wy)
		.def_readonly("wz",&RemoteFeedbackMru::wz)
		.def_readonly("wx_t",&RemoteFeedbackMru::wx_t)
		.def_readonly("wy_t",&RemoteFeedbackMru::wy_t)
		.def_readonly("wz_t",&RemoteFeedbackMru::wz_t)
		.def_readonly("x_t",&RemoteFeedbackMru::x_t)
		.def_readonly("y_t",&RemoteFeedbackMru::y_t)
		.def_readonly("z_t",&RemoteFeedbackMru::z_t)
		.def_readonly("x_tt",&RemoteFeedbackMru::x_tt)
		.def_readonly("y_tt",&RemoteFeedbackMru::y_tt)
		.def_readonly("z_tt",&RemoteFeedbackMru::z_tt);
	
	py::class_<RemoteFeedback>(m, "RemoteFeedback")
		.def(py::init<>())
		.def_readonly("t", &RemoteFeedback::t)
		.def_readonly("em8000", &RemoteFeedback::em8000)
		.def_readonly("em1500", &RemoteFeedback::em1500)
		.def_readonly("comau", &RemoteFeedback::comau)
		.def_readonly("at960", &RemoteFeedback::at960)
		.def_readonly("mru1", &RemoteFeedback::mru1)
		.def_readonly("mru2", &RemoteFeedback::mru2);



	// Control structs
	py::class_<RemoteControlComau>(m, "RemoteControlComau")
		.def(py::init<>())
		.def_readwrite("q1", &RemoteControlComau::q1)
		.def_readwrite("q2", &RemoteControlComau::q2)
		.def_readwrite("q3", &RemoteControlComau::q3)
		.def_readwrite("q4", &RemoteControlComau::q4)
		.def_readwrite("q5", &RemoteControlComau::q5)
		.def_readwrite("q6", &RemoteControlComau::q6)
		.def_readwrite("q1_t", &RemoteControlComau::q1_t)
		.def_readwrite("q2_t", &RemoteControlComau::q2_t)
		.def_readwrite("q3_t", &RemoteControlComau::q3_t)
		.def_readwrite("q4_t", &RemoteControlComau::q4_t)
		.def_readwrite("q5_t", &RemoteControlComau::q5_t)
		.def_readwrite("q6_t", &RemoteControlComau::q6_t)
		.def_readwrite("q1_tt", &RemoteControlComau::q1_tt)
		.def_readwrite("q2_tt", &RemoteControlComau::q2_tt)
		.def_readwrite("q3_tt", &RemoteControlComau::q3_tt)
		.def_readwrite("q4_tt", &RemoteControlComau::q4_tt)
		.def_readwrite("q5_tt", &RemoteControlComau::q5_tt)
		.def_readwrite("q6_tt", &RemoteControlComau::q6_tt);

	py::class_<RemoteControl>(m, "RemoteControl")
		.def(py::init<>())
		.def_readwrite("udp_key", &RemoteControl::udp_key)
		.def_readwrite("comau", &RemoteControl::comau);
	
	// Remote interface
	py::class_<RemoteInterface>(m, "RemoteInterface")
		.def(py::init<unsigned int>())
		.def("start", &RemoteInterface::start)
		.def("close", &RemoteInterface::close)
		.def("update", &RemoteInterface::update)
		.def("start_log", &RemoteInterface::start_log)
		.def("clear_log", &RemoteInterface::clear_log)
		.def("save_log", &RemoteInterface::save_log)
		.def_readonly("feedback", &RemoteInterface::feedback)
		.def_readwrite("control", &RemoteInterface::control);

	// Hmi interface
	py::class_<HmiInterface>(m, "HmiInterface")
		.def(py::init<unsigned int>())
		.def("start", &HmiInterface::start)
		.def("close", &HmiInterface::close)
		.def("update", &HmiInterface::update)
		.def("start_log", &HmiInterface::start_log)
		.def("clear_log", &HmiInterface::clear_log)
		.def("save_log", &HmiInterface::save_log)
		.def_readonly("feedback", &HmiInterface::feedback)
		.def_readwrite("control", &HmiInterface::control);
	
	// Return module
	return m.ptr();
}


int main(int argc, char** argv)
{	
	// Check for little or big endian
	int num = 1;
	if(*(char *)&num == 1)
	{	
		printf("\nLittle-Endian\n");
	}
	else
	{
		printf("Big-Endian\n");
	}


	return 0;
}