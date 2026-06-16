import 'dart:async';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:timezone/timezone.dart' as tz;
import '../data/countries.dart';

class ClockWidget extends StatefulWidget {
  final Country country;

  const ClockWidget({super.key, required this.country});

  @override
  State<ClockWidget> createState() => _ClockWidgetState();
}

class _ClockWidgetState extends State<ClockWidget> {
  late Timer _timer;
  late DateTime _now;

  @override
  void initState() {
    super.initState();
    _now = _getCurrentTime();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      setState(() {
        _now = _getCurrentTime();
      });
    });
  }

  @override
  void didUpdateWidget(ClockWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.country.timezone != widget.country.timezone) {
      setState(() {
        _now = _getCurrentTime();
      });
    }
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  DateTime _getCurrentTime() {
    try {
      final location = tz.getLocation(widget.country.timezone);
      final tzNow = tz.TZDateTime.now(location);
      return tzNow;
    } catch (_) {
      return DateTime.now();
    }
  }

  @override
  Widget build(BuildContext context) {
    final saatStr = DateFormat('HH:mm:ss').format(_now);
    final tarihStr = DateFormat('dd MMMM yyyy', 'tr_TR').format(_now);
    final gunStr = DateFormat('EEEE', 'tr_TR').format(_now);

    // UTC offset
    final offset = _now.timeZoneOffset;
    final hours = offset.inHours;
    final minutes = offset.inMinutes.abs() % 60;
    final sign = hours >= 0 ? '+' : '-';
    final utcStr = 'UTC$sign${hours.abs().toString().padLeft(2, '0')}:${minutes.toString().padLeft(2, '0')}';

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF1a1a2e), Color(0xFF16213e)],
        ),
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.4),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      padding: const EdgeInsets.symmetric(vertical: 36, horizontal: 24),
      child: Column(
        children: [
          // Bayrak + ülke adı
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(widget.country.flag, style: const TextStyle(fontSize: 28)),
              const SizedBox(width: 10),
              Flexible(
                child: Text(
                  widget.country.name,
                  style: const TextStyle(
                    color: Color(0xFFa0a0c0),
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          // Timezone + UTC offset
          Text(
            '${widget.country.timezone}  |  $utcStr',
            style: const TextStyle(
              color: Color(0xFFe0e0ff),
              fontSize: 12,
              letterSpacing: 0.5,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          // Dijital saat
          Text(
            saatStr,
            style: const TextStyle(
              color: Color(0xFF00d4ff),
              fontSize: 56,
              fontWeight: FontWeight.bold,
              fontFamily: 'monospace',
              letterSpacing: 6,
            ),
          ),
          const SizedBox(height: 12),
          // Gün ve tarih
          Text(
            '$gunStr, $tarihStr',
            style: const TextStyle(
              color: Color(0xFFc0c0e0),
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}
